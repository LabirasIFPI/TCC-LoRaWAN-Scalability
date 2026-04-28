/*
 * TCC Nícolas Rafael - Validação Empírica AU915 com 64 Canais Físicos
 *
 * Copyright (C) 2025 Nícolas Rafael Silva Alves
 * Este programa é software livre sob os termos da GPL v3.
 *
 * OBJETIVO: Provar empiricamente que o modelo de dilatação temporal
 * (multiplicar período por 64/3) é matematicamente equivalente a
 * instanciar fisicamente os 64 canais AU915 no simulador.
 *
 * MÉTODO: Este script bypassa o LorawanMacHelper e configura
 * diretamente o LogicalLoraChannelHelper com 64 canais, sem
 * necessidade de patch nos fontes do módulo lorawan.
 *
 * CENÁRIO: Apenas alocação estática (sem ADR), pois o ADR hardcoda
 * canais {0,1,2} no adr-component.cc e usa ChMask de 16 bits.
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
double simulationTime = 86400.0; // 24 horas
int appPeriod = 600;             // 10 minutos (1:1, SEM dilatação temporal)
double txPower = 30.0;           // AU915: 30 dBm (1 W EIRP)
int scenario = 1;                // 1 = Estático, 2 = ADR
std::string region = "BR";       // Fixado em BR (AU915) para este teste
bool enableAnim = false;         // Para compatibilidade com o script de execução

// Mapas de Rastreamento
std::map<uint32_t, double> packetsSent;
std::map<uint32_t, double> packetsRecv;
std::map<uint32_t, double> lastTxTime;
std::map<uint32_t, double> sumLatency;

long dropsUnderSensitivity = 0;
long dropsInterference = 0;
long dropsNoReceivers = 0;

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

// =========================================================================
// Configuração AU915 com 64 canais físicos
// =========================================================================
// Bypassa o LorawanMacHelper para configurar diretamente o channelHelper
// com 64 canais AU915 (902.3 + 0.2*k MHz, k=0..63).
// =========================================================================
Ptr<LogicalLoraChannelHelper>
CreateAu915ChannelHelper()
{
    // Criar helper com espaço para 64 canais uplink
    auto channelHelper = Create<LogicalLoraChannelHelper>(64);

    // Sub-band AU915 uplink: 902.3 - 914.9 MHz
    // Duty cycle = 1.0 (100%) — AU915 não tem restrição de duty cycle severa
    // MaxTxPower = 30 dBm (1 W EIRP para AU915)
    channelHelper->AddSubBand(Create<SubBand>(902000000, 915000000, 1.0, 30));

    // Instanciar os 64 canais uplink AU915
    // Frequência base: 902.3 MHz, espaçamento: 200 kHz
    // f(k) = 902300000 + k * 200000 Hz, para k = 0..63
    for (uint8_t k = 0; k < 64; ++k)
    {
        uint32_t freq = 902300000 + k * 200000;
        // DR0 (SF12) a DR5 (SF7) — mesma tabela EU868 (coincide com AU915 DR0-DR5)
        auto channel = Create<LogicalLoraChannel>(freq, 0, 5);
        channel->EnableForUplink();
        channelHelper->SetChannel(k, channel);
    }

    return channelHelper;
}

int main(int argc, char* argv[]) {
    CommandLine cmd;
    cmd.AddValue("nNodes", "Número de nós terminais", nNodes);
    cmd.AddValue("radius", "Raio da rede em metros", radius);
    cmd.AddValue("simulationTime", "Tempo de simulação em segundos", simulationTime);
    cmd.AddValue("scenario", "1=Estático, 2=ADR", scenario);
    cmd.AddValue("region", "EU (Europa) ou BR (Brasil)", region);
    cmd.AddValue("enableAnim", "Habilitar NetAnim (true/false)", enableAnim);
    cmd.Parse(argc, argv);

    std::cout << "\n=======================================================" << std::endl;
    std::cout << "  VALIDAÇÃO EMPÍRICA: 64 CANAIS AU915 FÍSICOS" << std::endl;
    std::cout << "  TCC Nícolas Rafael (LoRaWAN) - Cross-Check Model" << std::endl;
    std::cout << "=======================================================" << std::endl;
    std::cout << "  - Cenário:        Estático (SF por distância, SEM ADR)" << std::endl;
    std::cout << "  - Região:         Brasil (AU915 - 64 Canais FÍSICOS)" << std::endl;
    std::cout << "  - Potência TX:    " << txPower << " dBm" << std::endl;
    std::cout << "  - Qtd. de Nós:    " << nNodes << " dispositivos" << std::endl;
    std::cout << "  - Tempo Total:    " << simulationTime << "s (" << FormatSimulationTime(simulationTime) << ")" << std::endl;
    std::cout << "  - Período App:    " << appPeriod << "s (1:1, SEM dilatação)" << std::endl;
    std::cout << "  - Canais Uplink:  64 (902.3 a 914.9 MHz, 200 kHz step)" << std::endl;
    std::cout << "-------------------------------------------------------" << std::endl;

    double centerX = radius;
    double centerY = radius;

    // ========================
    // Criar nós
    // ========================
    NodeContainer endDevices;
    endDevices.Create(nNodes);
    NodeContainer gateways;
    gateways.Create(1);

    // ========================
    // Mobilidade
    // ========================
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

    // ========================
    // Canal de propagação (mesmo modelo da campanha principal)
    // ========================
    Ptr<LogDistancePropagationLossModel> loss = CreateObject<LogDistancePropagationLossModel>();
    loss->SetPathLossExponent(2.8);
    loss->SetReference(1.0, 46.37);

    Ptr<PropagationDelayModel> delay = CreateObject<ConstantSpeedPropagationDelayModel>();
    Ptr<LoraChannel> channel = CreateObject<LoraChannel>(loss, delay);

    // ========================
    // PHY Helper
    // ========================
    LoraPhyHelper phyHelper = LoraPhyHelper();
    phyHelper.SetChannel(channel);

    // ========================
    // MAC Helper (EU como base, depois sobrescrevemos os canais)
    // ========================
    LorawanMacHelper macHelper = LorawanMacHelper();
    macHelper.SetRegion(LorawanMacHelper::EU); // Base EU para ter as tabelas DR corretas

    LoraHelper helper = LoraHelper();

    // ========================
    // Instalar Gateway
    // ========================
    phyHelper.SetDeviceType(LoraPhyHelper::GW);
    macHelper.SetDeviceType(LorawanMacHelper::GW);
    helper.Install(phyHelper, macHelper, gateways);

    // Reconfigurar o Gateway para 64 canais AU915
    for (uint32_t i = 0; i < gateways.GetN(); ++i) {
        Ptr<LoraNetDevice> gwNetDev = gateways.Get(i)->GetDevice(0)->GetObject<LoraNetDevice>();
        Ptr<GatewayLoraPhy> gwPhy = gwNetDev->GetPhy()->GetObject<GatewayLoraPhy>();

        // Traces de monitoramento
        gwPhy->TraceConnectWithoutContext("UnderSensitivity", MakeCallback(&OnUnderSensitivity));
        gwPhy->TraceConnectWithoutContext("Interfered", MakeCallback(&OnInterfered));
        gwPhy->TraceConnectWithoutContext("NoReceivers", MakeCallback(&OnNoReceivers));

        // Resetar reception paths do EU padrão
        gwPhy->ResetReceptionPaths();

        // Adicionar todas as 64 frequências AU915 ao gateway
        for (uint8_t k = 0; k < 64; ++k)
        {
            uint32_t freq = 902300000 + k * 200000;
            gwPhy->AddFrequency(freq);
        }

        // Adicionar 8 reception paths (demoduladores SX1301 típicos)
        for (int rp = 0; rp < 8; ++rp)
        {
            gwPhy->AddReceptionPath();
        }

        // Sobrescrever o channelHelper do GW MAC para AU915
        Ptr<GatewayLorawanMac> gwMac = gwNetDev->GetMac()->GetObject<GatewayLorawanMac>();
        gwMac->SetLogicalLoraChannelHelper(CreateAu915ChannelHelper());
    }

    // ========================
    // Instalar End Devices
    // ========================
    phyHelper.SetDeviceType(LoraPhyHelper::ED);
    macHelper.SetDeviceType(LorawanMacHelper::ED_A);
    NetDeviceContainer endDevicesNetDevices = helper.Install(phyHelper, macHelper, endDevices);

    // Reconfigurar cada End Device para AU915
    for (uint32_t i = 0; i < endDevicesNetDevices.GetN(); ++i) {
        Ptr<LoraNetDevice> loraNetDevice = endDevicesNetDevices.Get(i)->GetObject<LoraNetDevice>();
        Ptr<ClassAEndDeviceLorawanMac> mac = loraNetDevice->GetMac()->GetObject<ClassAEndDeviceLorawanMac>();
        Ptr<Node> node = loraNetDevice->GetNode();

        // Trace para contagem de pacotes enviados
        mac->TraceConnectWithoutContext("SentNewPacket", MakeCallback(&OnTxPacket));

        // Endereço único
        uint32_t uniqueDevAddr = node->GetId() + 1;
        mac->SetDeviceAddress(LoraDeviceAddress(uniqueDevAddr));

        // *** SOBRESCREVER channelHelper com AU915 de 64 canais ***
        mac->SetLogicalLoraChannelHelper(CreateAu915ChannelHelper());

        // Alocação estática de SF por distância (mesmos limiares da campanha)
        mac->SetMType(LorawanMacHeader::UNCONFIRMED_DATA_UP);
        Ptr<MobilityModel> mm = node->GetObject<MobilityModel>();
        double distance = mm->GetDistanceFrom(gateways.Get(0)->GetObject<MobilityModel>());

        // Mesmos limiares de distância do script principal (30 dBm TX)
        int dr = 0;
        if (distance < 1330) dr = 5;       // SF7 (DR5)
        else if (distance < 1690) dr = 4;  // SF8 (DR4)
        else if (distance < 2150) dr = 3;  // SF9 (DR3)
        else if (distance < 2720) dr = 2;  // SF10 (DR2)
        else if (distance < 3320) dr = 1;  // SF11 (DR1)
        // else dr = 0;                    // SF12 (DR0) - default

        mac->SetDataRate(dr);
        mac->SetTransmissionPowerDbm(txPower);

        // Desabilitar ADR no end device se cenário for 1
        mac->SetAttribute("ADR", BooleanValue(scenario == 2));
    }

    // ========================
    // Network Server (sem ADR)
    // ========================
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
    nsHelper.EnableAdr(scenario == 2); // ADR conforme cenário

    ApplicationContainer nsApp = nsHelper.Install(networkServer.Get(0));
    nsApp.Get(0)->TraceConnectWithoutContext("ReceivedPacket", MakeCallback(&OnRxPacket));

    // ========================
    // Aplicação periódica (período REAL, sem dilatação)
    // ========================
    PeriodicSenderHelper appHelper;
    appHelper.SetPeriod(Seconds(appPeriod));
    appHelper.SetPacketSize(51);
    ApplicationContainer appContainer = appHelper.Install(endDevices);

    Ptr<UniformRandomVariable> x = CreateObject<UniformRandomVariable>();
    x->SetAttribute("Min", DoubleValue(0.0));
    x->SetAttribute("Max", DoubleValue(appPeriod));
    appContainer.StartWithJitter(Seconds(0), x);

    // ========================
    // Modelo de Energia
    // ========================
    BasicEnergySourceHelper basicSourceHelper;
    basicSourceHelper.Set("BasicEnergySourceInitialEnergyJ", DoubleValue(10000.0));
    basicSourceHelper.Set("BasicEnergySupplyVoltageV", DoubleValue(3.3));

    LoraRadioEnergyModelHelper radioEnergyHelper;
    radioEnergyHelper.Set("TxCurrentA", DoubleValue(0.35)); // AU915 30dBm
    radioEnergyHelper.Set("RxCurrentA", DoubleValue(0.0112));
    radioEnergyHelper.Set("StandbyCurrentA", DoubleValue(0.0014));
    radioEnergyHelper.Set("SleepCurrentA", DoubleValue(0.0000015));

    EnergySourceContainer sources = basicSourceHelper.Install(endDevices);
    DeviceEnergyModelContainer deviceModels = radioEnergyHelper.Install(endDevicesNetDevices, sources);

    // ========================
    // Simulação
    // ========================
    Simulator::Stop(Seconds(simulationTime));
    auto startWallClock = std::chrono::high_resolution_clock::now();
    Simulator::Run();
    auto endWallClock = std::chrono::high_resolution_clock::now();

    std::chrono::duration<double> elapsed = endWallClock - startWallClock;
    double execTimeSecs = elapsed.count();

    // ========================
    // Métricas
    // ========================
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

    long rawLost = (long)globalSent - (long)globalRecv;
    long realAlohaCollisions = rawLost - dropsUnderSensitivity - dropsNoReceivers;
    if (realAlohaCollisions < 0) realAlohaCollisions = 0;

    std::cout << "=======================================================" << std::endl;
    std::cout << "  RESULTADOS - VALIDAÇÃO 64 CANAIS AU915 FÍSICOS" << std::endl;
    std::cout << "=======================================================" << std::endl;
    std::cout << "  Tempo de Execução Real: " << execTimeSecs << " segundos" << std::endl;
    std::cout << "==== RESULTADOS DE REDE E ENERGIA ====" << std::endl;
    std::cout << "   - Pacotes Enviados: " << (long)globalSent << std::endl;
    std::cout << "   - Pacotes Recebidos: " << (long)globalRecv << std::endl;
    std::cout << "   - PDR Global:       " << globalPdr << " %" << std::endl;
    std::cout << "   - Índice Jain:      " << jainIndex << std::endl;
    std::cout << "   - Consumo Médio:    " << avgEnergy << " Joules/Nó" << std::endl;
    std::cout << "   - Latência Média:   " << avgLatency << " segundos" << std::endl;
    std::cout << "==== RAIO-X DE PERDAS (GATEWAY PHY) ====" << std::endl;
    std::cout << "   - Saturação (Sem Demoduladores): " << dropsNoReceivers << " pacotes" << std::endl;
    std::cout << "   - Colisões (ALOHA no Ar):        " << realAlohaCollisions << " pacotes" << std::endl;
    std::cout << "   - Bloqueio (Sinal Fraco):        " << dropsUnderSensitivity << " pacotes" << std::endl;
    std::cout << "==== DISTRIBUIÇÃO FINAL DE DR/SF ====" << std::endl;
    std::cout << "   - SF12 (DR0): " << drCount[0] << " nós | SF11 (DR1): " << drCount[1] << " nós" << std::endl;
    std::cout << "   - SF10 (DR2): " << drCount[2] << " nós | SF9  (DR3): " << drCount[3] << " nós" << std::endl;
    std::cout << "   - SF8  (DR4): " << drCount[4] << " nós | SF7  (DR5): " << drCount[5] << " nós" << std::endl;
    std::cout << "=======================================================" << std::endl;

    // Saída CSV compatível com o formato da campanha principal
    // Formato: [RES_VAL],Regiao,Cenario,Nos,EnergiaTotal,EnergiaMédia,PDR,Jain,TempoExec,Latencia,Colisoes,SinalFraco,Saturacao,DR0..DR5
    std::cout << "[RES_VAL],BR_64CH," << scenario << "," << nNodes << "," << totalConsumed << "," << avgEnergy
              << "," << globalPdr << "," << jainIndex << "," << execTimeSecs << "," << avgLatency
              << "," << realAlohaCollisions << "," << dropsUnderSensitivity
              << "," << dropsNoReceivers
              << "," << drCount[0] << "," << drCount[1] << "," << drCount[2]
              << "," << drCount[3] << "," << drCount[4] << "," << drCount[5] << std::endl;

    Simulator::Destroy();
    return 0;
}
