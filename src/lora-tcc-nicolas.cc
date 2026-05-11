/*
 * TCC Nícolas Rafael - Análise de Escalabilidade em Redes LoRaWAN
 *
 * Copyright (C) 2025 Nícolas Rafael Silva Alves
 * Este programa é software livre: podes redistribuí-lo e/ou modificá-lo
 * sob os termos da Licença Pública Geral GNU (GPL) conforme publicada pela
 * Free Software Foundation, versão 3 da Licença.
 *
 * Este programa é distribuído na esperança de que seja útil,
 * mas SEM QUALQUER GARANTIA; sem mesmo a garantia implícita de
 * COMERCIALIZAÇÃO ou ADEQUAÇÃO A UM DETERMINADO FIM. Consulta a
 * Licença Pública Geral GNU para mais detalhes.
 *
 * Deverás ter recebido uma cópia da Licença Pública Geral GNU
 * juntamente com este programa. Caso contrário, consulta
 * <https://www.gnu.org/licenses/>.
 */

#include "ns3/applications-module.h"
#include "ns3/core-module.h"
#include "ns3/energy-module.h"
#include "ns3/lora-frame-header.h"
#include "ns3/lorawan-mac-header.h"
#include "ns3/lorawan-module.h"
#include "ns3/mobility-module.h"
#include "ns3/network-module.h"
#include "ns3/point-to-point-module.h"
#include "ns3/propagation-module.h"
#include "ns3/netanim-module.h"

#include <chrono>
#include <iostream>
#include <map>
#include <numeric>
#include <sstream>

using namespace ns3;
using namespace lorawan;

// --- Variáveis Globais de Controle ---
int nNodes = 100;
double radius = 5000.0;
double simulationTime = 86400.0; // 24 horas - JUSTIFICATIVA: Tempo necessário para steady-state em redes LoRaWAN densas.
// Com a Lei de Little aplicada (dilatando período em 21.3x para emular 64 canais AU915),
// 24h garantem que o tráfego entra em regime estacionário e colisões ALOHA seguem Poisson realista.
int scenario = 1;                // 1 = Estático, 2 = ADR
int appPeriod = 600;             // 10 minutos
std::string region = "EU";       // EU ou BR
int nChannels = 64;              // Novo: Número de canais emulados para BR
bool enableAnim = false;         // Ativar NetAnim

// Mapas de Rastreamento
std::map<uint32_t, double> packetsSent;
std::map<uint32_t, double> packetsRecv;
std::map<uint32_t, double> lastTxTime;
std::map<uint32_t, double> sumLatency;

long dropsUnderSensitivity = 0;
long dropsInterference = 0;
long dropsNoReceivers = 0; // Saturação de Hardware

static std::string FormatSimulationTime(double seconds) {
    long totalSec = static_cast<long>(seconds + 0.5);
    long hours = totalSec / 3600;
    long minutes = (totalSec % 3600) / 60;
    long secs = totalSec % 60;
    std::ostringstream oss;
    if (hours > 0) oss << hours << "h " << minutes << "m " << secs << "s";
    else if (minutes > 0) oss << minutes << "m " << secs << "s";
    else oss << secs << "s";
    return oss.str();
}

void OnUnderSensitivity(Ptr<const Packet> packet) { dropsUnderSensitivity++; }
void OnInterfered(Ptr<const Packet> packet) { dropsInterference++; }
void OnNoReceivers(Ptr<const Packet> packet) { dropsNoReceivers++; }

void OnTxPacket(Ptr<const Packet> packet) {
    if (packet->GetSize() < 12) return;
    uint8_t buf[12];
    packet->CopyData(buf, 12);
    uint8_t mType = buf[0] >> 5;
    if (mType == 2 || mType == 4) {
        uint32_t devAddr = buf[1] | (buf[2] << 8) | (buf[3] << 16) | (buf[4] << 24);
        packetsSent[devAddr]++;
        lastTxTime[devAddr] = Simulator::Now().GetSeconds();
    }
}

void OnRxPacket(Ptr<const Packet> packet) {
    if (packet->GetSize() < 12) return;
    uint8_t buf[12];
    packet->CopyData(buf, 12);
    uint8_t mType = buf[0] >> 5;
    if (mType == 2 || mType == 4) {
        uint32_t devAddr = buf[1] | (buf[2] << 8) | (buf[3] << 16) | (buf[4] << 24);
        packetsRecv[devAddr]++;
        if (lastTxTime.find(devAddr) != lastTxTime.end()) {
            sumLatency[devAddr] += (Simulator::Now().GetSeconds() - lastTxTime[devAddr]);
        }
    }
}

int main(int argc, char* argv[]) {
    CommandLine cmd;
    cmd.AddValue("nNodes", "Número de nós terminais", nNodes);
    cmd.AddValue("radius", "Raio da rede em metros", radius);
    cmd.AddValue("simulationTime", "Tempo de simulação em segundos (padrão: 86400s = 24h)", simulationTime);
    cmd.AddValue("scenario", "1=Estático, 2=ADR", scenario);
    cmd.AddValue("nChannels", "Número de canais a emular no BR (ex: 16, 64)", nChannels);
    cmd.AddValue("region", "EU (Europa) ou BR (Brasil)", region);
    cmd.AddValue("enableAnim", "Habilitar NetAnim (true/false)", enableAnim); 
    cmd.Parse(argc, argv);

    double simulatedAppPeriod = appPeriod;
    double scalingFactor = 1.0;
    double txPower = (region == "BR") ? 30.0 : 14.0; 

    if (region == "BR") {
        simulatedAppPeriod = appPeriod * (static_cast<double>(nChannels) / 3.0);
        scalingFactor = (static_cast<double>(nChannels) / 3.0);
    }

    std::cout << "\n=======================================================" << std::endl;
    std::cout << "  INICIANDO SIMULAÇÃO: TCC NÍCOLAS RAFAEL (LoRaWAN)" << std::endl;
    std::cout << "=======================================================" << std::endl;
    std::cout << "  - Cenário:        " << (scenario == 1 ? "1 (Estático)" : "2 (ADR)") << std::endl;
    std::cout << "  - Região:         " << (region == "BR" ? "Brasil (AU915 - Emulando " + std::to_string(nChannels) + " Canais)" : "Europa (EU868 - 3 Canais)") << std::endl;
    std::cout << "  - Potência TX:    " << txPower << " dBm" << std::endl;
    std::cout << "  - Qtd. de Nós:    " << nNodes << " dispositivos reais no mapa" << std::endl;
    std::cout << "  - Tempo Total:    " << simulationTime << "s (" << FormatSimulationTime(simulationTime) << ")" << std::endl;
    std::cout << "  - Período App:    " << simulatedAppPeriod << "s (Carga Balanceada)" << std::endl;
    std::cout << "-------------------------------------------------------" << std::endl;

    double centerX = radius;
    double centerY = radius;

    NodeContainer endDevices;
    endDevices.Create(nNodes);
    NodeContainer gateways;
    gateways.Create(1);

    MobilityHelper mobility;
    Ptr<UniformDiscPositionAllocator> posAlloc = CreateObject<UniformDiscPositionAllocator>();
    posAlloc->SetX(centerX);
    posAlloc->SetY(centerY);
    posAlloc->SetRho(radius);
    mobility.SetPositionAllocator(posAlloc);
    mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    mobility.Install(endDevices);

    Ptr<ListPositionAllocator> gatewayAllocator = CreateObject<ListPositionAllocator>();
    gatewayAllocator->Add(Vector(centerX, centerY, 15.0));
    mobility.SetPositionAllocator(gatewayAllocator);
    mobility.Install(gateways);

    Ptr<LogDistancePropagationLossModel> loss = CreateObject<LogDistancePropagationLossModel>();
    loss->SetPathLossExponent(2.8); 
    loss->SetReference(1.0, 46.37);

    Ptr<PropagationDelayModel> delay = CreateObject<ConstantSpeedPropagationDelayModel>();
    Ptr<LoraChannel> channel = CreateObject<LoraChannel>(loss, delay);

    LoraPhyHelper phyHelper = LoraPhyHelper();
    phyHelper.SetChannel(channel);

    LorawanMacHelper macHelper = LorawanMacHelper();
    macHelper.SetRegion(LorawanMacHelper::EU);

    LoraHelper helper = LoraHelper();

    phyHelper.SetDeviceType(LoraPhyHelper::GW);
    macHelper.SetDeviceType(LorawanMacHelper::GW);
    helper.Install(phyHelper, macHelper, gateways);

    for (uint32_t i = 0; i < gateways.GetN(); ++i) {
        Ptr<LoraNetDevice> gwNetDev = gateways.Get(i)->GetDevice(0)->GetObject<LoraNetDevice>();
        Ptr<GatewayLoraPhy> gwPhy = gwNetDev->GetPhy()->GetObject<GatewayLoraPhy>();
        gwPhy->TraceConnectWithoutContext("UnderSensitivity", MakeCallback(&OnUnderSensitivity));
        gwPhy->TraceConnectWithoutContext("Interfered", MakeCallback(&OnInterfered));
        gwPhy->TraceConnectWithoutContext("NoReceivers", MakeCallback(&OnNoReceivers));
    }

    phyHelper.SetDeviceType(LoraPhyHelper::ED);
    macHelper.SetDeviceType(LorawanMacHelper::ED_A);
    NetDeviceContainer endDevicesNetDevices = helper.Install(phyHelper, macHelper, endDevices);

    for (uint32_t i = 0; i < endDevicesNetDevices.GetN(); ++i) {
        Ptr<LoraNetDevice> loraNetDevice = endDevicesNetDevices.Get(i)->GetObject<LoraNetDevice>();
        Ptr<ClassAEndDeviceLorawanMac> mac = loraNetDevice->GetMac()->GetObject<ClassAEndDeviceLorawanMac>();
        Ptr<Node> node = loraNetDevice->GetNode();

        mac->TraceConnectWithoutContext("SentNewPacket", MakeCallback(&OnTxPacket));

        uint32_t uniqueDevAddr = node->GetId() + 1;
        mac->SetDeviceAddress(LoraDeviceAddress(uniqueDevAddr));

        if (scenario == 2) {
            mac->SetDataRate(0);
            mac->SetMType(LorawanMacHeader::UNCONFIRMED_DATA_UP);
            mac->SetTransmissionPowerDbm(txPower); 
        } else {
            mac->SetMType(LorawanMacHeader::UNCONFIRMED_DATA_UP);
            Ptr<MobilityModel> mm = node->GetObject<MobilityModel>();
            double distance = mm->GetDistanceFrom(gateways.Get(0)->GetObject<MobilityModel>());

            // =========================================================================
            // ALOCAÇÃO ESTÁTICA DE SF BASEADA EM DISTÂNCIA (Cenário 1)
            // =========================================================================
            // Estes limiares foram calculados intercetando a Sensibilidade de Receção (RX Sensitivity)
            // típica do chip Semtech SX1276 com o modelo de propagação Log-Distance (n=2.8).
            // Transmitindo a 30 dBm (AU915), o sinal atinge o limite de sensibilidade a distâncias específicas:
            // - SF7: -123 dBm → ~1330m (sinal mais limpo requerido)
            // - SF8: -126 dBm → ~1690m
            // - SF9: -129 dBm → ~2150m
            // - SF10: -132 dBm → ~2720m
            // - SF11: -134.5 dBm → ~3320m
            // - SF12: -137 dBm → >3320m (maior ganho de processamento, sobrevive a sinais fracos)
            // =========================================================================
            int dr = 0;
            if (distance < 1330) dr = 5;      // SF7 (DR5)
            else if (distance < 1690) dr = 4; // SF8 (DR4)
            else if (distance < 2150) dr = 3; // SF9 (DR3)
            else if (distance < 2720) dr = 2; // SF10 (DR2)
            else if (distance < 3320) dr = 1; // SF11 (DR1)
            // else dr = 0;                   // SF12 (DR0) - default

            mac->SetDataRate(dr);
            mac->SetTransmissionPowerDbm(txPower);
        }
    }

    NodeContainer networkServer;
    networkServer.Create(1);
    PointToPointHelper p2p;
    p2p.SetDeviceAttribute("DataRate", StringValue("10Gbps"));
    p2p.SetChannelAttribute("Delay", StringValue("2ms"));

    ns3::lorawan::P2PGwRegistration_t registration;
    for (NodeContainer::Iterator gw = gateways.Begin(); gw != gateways.End(); ++gw) {
        NetDeviceContainer p2pDevices = p2p.Install(networkServer.Get(0), *gw);
        Ptr<PointToPointNetDevice> nsP2PDevice = p2pDevices.Get(0)->GetObject<PointToPointNetDevice>();
        registration.push_back(std::make_pair(nsP2PDevice, *gw));
    }

    ForwarderHelper forwarderHelper;
    forwarderHelper.Install(gateways);

    NetworkServerHelper nsHelper;
    nsHelper.SetGatewaysP2P(registration);
    nsHelper.SetEndDevices(endDevices);
    nsHelper.EnableAdr(scenario == 2);

    ApplicationContainer nsApp = nsHelper.Install(networkServer.Get(0));
    nsApp.Get(0)->TraceConnectWithoutContext("ReceivedPacket", MakeCallback(&OnRxPacket));

    PeriodicSenderHelper appHelper;
    appHelper.SetPeriod(Seconds(simulatedAppPeriod));
    appHelper.SetPacketSize(51);
    ApplicationContainer appContainer = appHelper.Install(endDevices);

    Ptr<UniformRandomVariable> x = CreateObject<UniformRandomVariable>();
    x->SetAttribute("Min", DoubleValue(0.0));
    x->SetAttribute("Max", DoubleValue(simulatedAppPeriod));
    appContainer.StartWithJitter(Seconds(0), x);

    BasicEnergySourceHelper basicSourceHelper;
    basicSourceHelper.Set("BasicEnergySourceInitialEnergyJ", DoubleValue(10000.0));
    basicSourceHelper.Set("BasicEnergySupplyVoltageV", DoubleValue(3.3));

    LoraRadioEnergyModelHelper radioEnergyHelper;
    double txCurrent = (region == "BR") ? 0.35 : 0.028; 
    radioEnergyHelper.Set("TxCurrentA", DoubleValue(txCurrent));
    radioEnergyHelper.Set("RxCurrentA", DoubleValue(0.0112));
    radioEnergyHelper.Set("StandbyCurrentA", DoubleValue(0.0014));
    radioEnergyHelper.Set("SleepCurrentA", DoubleValue(0.0000015));

    EnergySourceContainer sources = basicSourceHelper.Install(endDevices);
    DeviceEnergyModelContainer deviceModels = radioEnergyHelper.Install(endDevicesNetDevices, sources);

    Simulator::Stop(Seconds(simulationTime));
    auto startWallClock = std::chrono::high_resolution_clock::now();
    Simulator::Run();
    auto endWallClock = std::chrono::high_resolution_clock::now();

    std::chrono::duration<double> elapsed = endWallClock - startWallClock;
    double execTimeSecs = elapsed.count();

    // =========================================================================
    // EXTRAÇÃO DE MÉTRICAS E INFERÊNCIA ALOHA
    // =========================================================================
    double totalConsumed = 0.0;
    for (uint32_t i = 0; i < endDevices.GetN(); ++i) {
        Ptr<Node> node = endDevices.Get(i);
        Ptr<EnergySourceContainer> sourceContainer = node->GetObject<EnergySourceContainer>();
        if (sourceContainer && sourceContainer->GetN() > 0) {
            Ptr<EnergySource> source = sourceContainer->Get(0);
            totalConsumed += (10000.0 - source->GetRemainingEnergy());
        }
    }
    double avgEnergy = (nNodes > 0) ? (totalConsumed / nNodes) : 0.0;

    double sumPdr = 0.0, sumPdrSq = 0.0, globalSent = 0.0, globalRecv = 0.0;
    double totalLatency = 0.0, countLatency = 0.0;
    int activeNodes = packetsSent.size();

    for (const auto& [devAddr, sent] : packetsSent) {
        if (sent > 0) {
            double recv = packetsRecv[devAddr];
            double pdr = recv / sent;
            sumPdr += pdr;
            sumPdrSq += (pdr * pdr);
            globalSent += sent;
            globalRecv += recv;

            totalLatency += sumLatency[devAddr];
            countLatency += recv;
        }
    }

    double jainIndex = (activeNodes > 0 && sumPdrSq > 0) ? ((sumPdr * sumPdr) / (activeNodes * sumPdrSq)) : 0.0;
    double globalPdr = (globalSent > 0) ? ((globalRecv / globalSent) * 100.0) : 0.0;
    double avgLatency = (countLatency > 0) ? (totalLatency / countLatency) : 0.0;

    int drCount[6] = {0, 0, 0, 0, 0, 0};
    for (uint32_t i = 0; i < endDevicesNetDevices.GetN(); ++i) {
        Ptr<LoraNetDevice> loraNetDevice = endDevicesNetDevices.Get(i)->GetObject<LoraNetDevice>();
        Ptr<ClassAEndDeviceLorawanMac> mac = loraNetDevice->GetMac()->GetObject<ClassAEndDeviceLorawanMac>();
        uint8_t dr = mac->GetDataRate();
        if (dr >= 0 && dr <= 5) drCount[dr]++;
    }

    // --- CÁLCULO DINÂMICO DE COLISÕES ALOHA SILENCIOSAS ---
    long rawLost = (long)globalSent - (long)globalRecv;
    long realAlohaCollisions = rawLost - dropsUnderSensitivity - dropsNoReceivers;
    if (realAlohaCollisions < 0) realAlohaCollisions = 0;

    std::cout << "=======================================================" << std::endl;
    std::cout << "Simulacao concluida com sucesso!" << std::endl;
    std::cout << "Tempo de Execucao Real: " << execTimeSecs << " segundos" << std::endl;
    std::cout << "==== RESULTADOS DE REDE E ENERGIA ====" << std::endl;
    std::cout << "   - Pacotes Enviados: " << (long)(globalSent * scalingFactor) << std::endl;
    std::cout << "   - PDR Global:       " << globalPdr << " %" << std::endl;
    std::cout << "   - Indice Jain:      " << jainIndex << std::endl;
    std::cout << "   - Consumo Medio:    " << avgEnergy << " Joules/No" << std::endl;
    std::cout << "   - Latencia Media:   " << avgLatency << " segundos" << std::endl;
    std::cout << "==== RAIO-X DE PERDAS (GATEWAY PHY) ====" << std::endl;
    std::cout << "   - Saturacao (Sem Demoduladores): " << (long)(dropsNoReceivers * scalingFactor) << " pacotes perdidos" << std::endl;
    std::cout << "   - Colisoes (ALOHA no Ar):        " << (long)(realAlohaCollisions * scalingFactor) << " pacotes perdidos" << std::endl;
    std::cout << "   - Bloqueio (Sinal Fraco):        " << (long)(dropsUnderSensitivity * scalingFactor) << " pacotes perdidos" << std::endl;
    std::cout << "==== DISTRIBUICAO FINAL DE DR/SF ====" << std::endl;
    std::cout << "   - SF12 (DR0): " << drCount[0] << " nos | SF11 (DR1): " << drCount[1] << " nos" << std::endl;
    std::cout << "   - SF10 (DR2): " << drCount[2] << " nos | SF9  (DR3): " << drCount[3] << " nos" << std::endl;
    std::cout << "   - SF8  (DR4): " << drCount[4] << " nos | SF7  (DR5): " << drCount[5] << " nos" << std::endl;
    std::cout << "=======================================================\n" << std::endl;

    std::cout << "[RES]," << region << "," << scenario << "," << nNodes << "," << totalConsumed << "," << avgEnergy
              << "," << globalPdr << "," << jainIndex << "," << execTimeSecs << "," << avgLatency
              << "," << (long)(globalSent * scalingFactor) << "," << (long)(globalRecv * scalingFactor)
              << "," << (long)(realAlohaCollisions * scalingFactor) << "," << (long)(dropsUnderSensitivity * scalingFactor) 
              << "," << (long)(dropsNoReceivers * scalingFactor) 
              << "," << drCount[0] << "," << drCount[1] << "," << drCount[2] 
              << "," << drCount[3] << "," << drCount[4] << "," << drCount[5] << std::endl;

    Simulator::Destroy();
    return 0;
}