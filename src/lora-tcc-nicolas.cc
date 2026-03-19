/*
 * Copyright (C) 2025 Nícolas Rafael Silva Alves
 * TCC Nícolas Rafael - Análise de Escalabilidade em Redes LoRaWAN
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
int scenario = 1;                // 1 = Estático, 2 = ADR
int appPeriod = 600;             // 10 minutos

// Mapas de Rastreamento
std::map<uint32_t, double> packetsSent;
std::map<uint32_t, double> packetsRecv;

// NOVAS MÉTRICAS: Latência e Motivo de Perda
std::map<uint32_t, double> lastTxTime;
std::map<uint32_t, double> sumLatency;
long dropsUnderSensitivity = 0;
long dropsInterference = 0;

static std::string
FormatSimulationTime(double seconds)
{
    long totalSec = static_cast<long>(seconds + 0.5);
    long hours = totalSec / 3600;
    long minutes = (totalSec % 3600) / 60;
    long secs = totalSec % 60;
    std::ostringstream oss;
    if (hours > 0)
    {
        oss << hours << "h " << minutes << "m " << secs << "s";
    }
    else if (minutes > 0)
    {
        oss << minutes << "m " << secs << "s";
    }
    else
    {
        oss << secs << "s";
    }
    return oss.str();
}

// Callbacks de Falha na Antena (Gateway)
void
OnUnderSensitivity(Ptr<const Packet> packet)
{
    dropsUnderSensitivity++;
}

void
OnInterfered(Ptr<const Packet> packet)
{
    dropsInterference++;
}

// Callbacks de Sucesso
void
OnTxPacket(Ptr<const Packet> packet)
{
    if (packet->GetSize() < 12)
    {
        return;
    }
    uint8_t buf[12];
    packet->CopyData(buf, 12);
    uint8_t mType = buf[0] >> 5;
    if (mType == 2 || mType == 4)
    {
        uint32_t devAddr = buf[1] | (buf[2] << 8) | (buf[3] << 16) | (buf[4] << 24);
        packetsSent[devAddr]++;
        // Registra o tempo exato do envio para o cálculo de latência
        lastTxTime[devAddr] = Simulator::Now().GetSeconds();
    }
}

void
OnRxPacket(Ptr<const Packet> packet)
{
    if (packet->GetSize() < 12)
    {
        return;
    }
    uint8_t buf[12];
    packet->CopyData(buf, 12);
    uint8_t mType = buf[0] >> 5;
    if (mType == 2 || mType == 4)
    {
        uint32_t devAddr = buf[1] | (buf[2] << 8) | (buf[3] << 16) | (buf[4] << 24);
        packetsRecv[devAddr]++;
        // Calcula a latência (ToA) baseada no carimbo de envio
        if (lastTxTime.find(devAddr) != lastTxTime.end())
        {
            sumLatency[devAddr] += (Simulator::Now().GetSeconds() - lastTxTime[devAddr]);
        }
    }
}

int
main(int argc, char* argv[])
{
    CommandLine cmd;
    cmd.AddValue("nNodes", "Número de nós terminais", nNodes);
    cmd.AddValue("scenario", "1=Estático, 2=ADR", scenario);
    cmd.Parse(argc, argv);

    std::cout << "\n=======================================================" << std::endl;
    std::cout << "  INICIANDO SIMULAÇÃO: TCC NÍCOLAS RAFAEL (LoRaWAN)" << std::endl;
    std::cout << "=======================================================" << std::endl;
    std::cout << "  - Cenário:        " << (scenario == 1 ? "1 (Estático)" : "2 (ADR)")
              << std::endl;
    std::cout << "  - Qtd. de Nós:    " << nNodes << " dispositivos" << std::endl;
    std::cout << "  - Tempo Total:    " << simulationTime << "s ("
              << FormatSimulationTime(simulationTime) << ")" << std::endl;
    std::cout << "-------------------------------------------------------" << std::endl;

    NodeContainer endDevices;
    endDevices.Create(nNodes);
    NodeContainer gateways;
    gateways.Create(1);

    MobilityHelper mobility;
    Ptr<UniformDiscPositionAllocator> posAlloc = CreateObject<UniformDiscPositionAllocator>();
    posAlloc->SetX(0.0);
    posAlloc->SetY(0.0);
    posAlloc->SetRho(radius);
    mobility.SetPositionAllocator(posAlloc);
    mobility.SetMobilityModel("ns3::ConstantPositionMobilityModel");
    mobility.Install(endDevices);

    Ptr<ListPositionAllocator> gatewayAllocator = CreateObject<ListPositionAllocator>();
    gatewayAllocator->Add(Vector(0.0, 0.0, 15.0));
    mobility.SetPositionAllocator(gatewayAllocator);
    mobility.Install(gateways);

    Ptr<LogDistancePropagationLossModel> loss = CreateObject<LogDistancePropagationLossModel>();
    loss->SetPathLossExponent(3.76); // Urbano Denso
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

    // Instala e conecta rastreadores de perda na Antena do Gateway
    for (uint32_t i = 0; i < gateways.GetN(); ++i)
    {
        Ptr<LoraNetDevice> gwNetDev = gateways.Get(i)->GetDevice(0)->GetObject<LoraNetDevice>();
        Ptr<LoraPhy> phy = gwNetDev->GetPhy();
        phy->TraceConnectWithoutContext("UnderSensitivity", MakeCallback(&OnUnderSensitivity));
        phy->TraceConnectWithoutContext("Interfered", MakeCallback(&OnInterfered));
    }

    phyHelper.SetDeviceType(LoraPhyHelper::ED);
    macHelper.SetDeviceType(LorawanMacHelper::ED_A);
    NetDeviceContainer endDevicesNetDevices = helper.Install(phyHelper, macHelper, endDevices);

    for (uint32_t i = 0; i < endDevicesNetDevices.GetN(); ++i)
    {
        Ptr<LoraNetDevice> loraNetDevice = endDevicesNetDevices.Get(i)->GetObject<LoraNetDevice>();
        Ptr<ClassAEndDeviceLorawanMac> mac =
            loraNetDevice->GetMac()->GetObject<ClassAEndDeviceLorawanMac>();
        Ptr<Node> node = loraNetDevice->GetNode();

        mac->TraceConnectWithoutContext("SentNewPacket", MakeCallback(&OnTxPacket));

        uint32_t uniqueDevAddr = node->GetId() + 1;
        mac->SetDeviceAddress(LoraDeviceAddress(uniqueDevAddr));

        if (scenario == 2)
        {
            mac->SetDataRate(0);
            mac->SetMType(LorawanMacHeader::UNCONFIRMED_DATA_UP);
        }
        else
        {
            mac->SetMType(LorawanMacHeader::UNCONFIRMED_DATA_UP);
            Ptr<MobilityModel> mm = node->GetObject<MobilityModel>();
            double distance = mm->GetDistanceFrom(gateways.Get(0)->GetObject<MobilityModel>());

            int dr = 0;
            if (distance < 1330)
            {
                dr = 5;
            }
            else if (distance < 1690)
            {
                dr = 4;
            }
            else if (distance < 2150)
            {
                dr = 3;
            }
            else if (distance < 2720)
            {
                dr = 2;
            }
            else if (distance < 3320)
            {
                dr = 1;
            }

            mac->SetDataRate(dr);
            mac->SetTransmissionPowerDbm(14);
        }
    }

    NodeContainer networkServer;
    networkServer.Create(1);
    PointToPointHelper p2p;
    p2p.SetDeviceAttribute("DataRate", StringValue("10Gbps"));
    p2p.SetChannelAttribute("Delay", StringValue("2ms"));

    ns3::lorawan::P2PGwRegistration_t registration;
    for (NodeContainer::Iterator gw = gateways.Begin(); gw != gateways.End(); ++gw)
    {
        NetDeviceContainer p2pDevices = p2p.Install(networkServer.Get(0), *gw);
        Ptr<PointToPointNetDevice> nsP2PDevice =
            p2pDevices.Get(0)->GetObject<PointToPointNetDevice>();
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
    appHelper.SetPeriod(Seconds(appPeriod));
    appHelper.SetPacketSize(51);
    ApplicationContainer appContainer = appHelper.Install(endDevices);

    Ptr<UniformRandomVariable> x = CreateObject<UniformRandomVariable>();
    x->SetAttribute("Min", DoubleValue(0.0));
    x->SetAttribute("Max", DoubleValue(appPeriod));
    appContainer.StartWithJitter(Seconds(0), x);

    BasicEnergySourceHelper basicSourceHelper;
    basicSourceHelper.Set("BasicEnergySourceInitialEnergyJ", DoubleValue(10000.0));
    basicSourceHelper.Set("BasicEnergySupplyVoltageV", DoubleValue(3.3));

    LoraRadioEnergyModelHelper radioEnergyHelper;
    radioEnergyHelper.Set("TxCurrentA", DoubleValue(0.028));
    radioEnergyHelper.Set("RxCurrentA", DoubleValue(0.0112));
    radioEnergyHelper.Set("StandbyCurrentA", DoubleValue(0.0014));
    radioEnergyHelper.Set("SleepCurrentA", DoubleValue(0.0000015));

    EnergySourceContainer sources = basicSourceHelper.Install(endDevices);
    DeviceEnergyModelContainer deviceModels =
        radioEnergyHelper.Install(endDevicesNetDevices, sources);

    Simulator::Stop(Seconds(simulationTime));

    auto startWallClock = std::chrono::high_resolution_clock::now();
    Simulator::Run();
    auto endWallClock = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = endWallClock - startWallClock;
    double execTimeSecs = elapsed.count();

    // =========================================================================
    // EXTRAÇÃO FINAL DE MÉTRICAS (Energia, Rede, Latência e ADR)
    // =========================================================================

    // 1. Cálculo de Energia
    double totalConsumed = 0.0;
    for (uint32_t i = 0; i < endDevices.GetN(); ++i)
    {
        Ptr<Node> node = endDevices.Get(i);
        Ptr<EnergySourceContainer> sourceContainer = node->GetObject<EnergySourceContainer>();
        if (sourceContainer && sourceContainer->GetN() > 0)
        {
            Ptr<EnergySource> source = sourceContainer->Get(0);
            totalConsumed += (10000.0 - source->GetRemainingEnergy());
        }
    }
    double avgEnergy = (nNodes > 0) ? (totalConsumed / nNodes) : 0.0;

    // 2. Cálculo de Rede (PDR, Jain e Latência)
    double sumPdr = 0.0, sumPdrSq = 0.0, globalSent = 0.0, globalRecv = 0.0;
    double totalLatency = 0.0, countLatency = 0.0;
    int activeNodes = packetsSent.size();

    for (const auto& [devAddr, sent] : packetsSent)
    {
        if (sent > 0)
        {
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

    double jainIndex =
        (activeNodes > 0 && sumPdrSq > 0) ? ((sumPdr * sumPdr) / (activeNodes * sumPdrSq)) : 0.0;
    double globalPdr = (globalSent > 0) ? ((globalRecv / globalSent) * 100.0) : 0.0;
    double avgLatency = (countLatency > 0) ? (totalLatency / countLatency) : 0.0;

    // 3. Extração da Distribuição Final de SF (ADR Monitor)
    // drCount[0]=SF12, drCount[1]=SF11, drCount[2]=SF10, drCount[3]=SF9, drCount[4]=SF8,
    // drCount[5]=SF7
    int drCount[6] = {0, 0, 0, 0, 0, 0};
    for (uint32_t i = 0; i < endDevicesNetDevices.GetN(); ++i)
    {
        Ptr<LoraNetDevice> loraNetDevice = endDevicesNetDevices.Get(i)->GetObject<LoraNetDevice>();
        Ptr<ClassAEndDeviceLorawanMac> mac =
            loraNetDevice->GetMac()->GetObject<ClassAEndDeviceLorawanMac>();
        uint8_t dr = mac->GetDataRate();
        if (dr >= 0 && dr <= 5)
        {
            drCount[dr]++;
        }
    }

    // =========================================================================
    // IMPRESSÃO DOS RESULTADOS
    // =========================================================================
    std::cout << "=======================================================" << std::endl;
    std::cout << "Simulação concluída com sucesso!" << std::endl;
    std::cout << "==== RESULTADOS DE REDE E ENERGIA ====" << std::endl;
    std::cout << "   - Pacotes Enviados: " << globalSent << std::endl;
    std::cout << "   - PDR Global:       " << globalPdr << " %" << std::endl;
    std::cout << "   - Índice Jain:      " << jainIndex << std::endl;
    std::cout << "   - Consumo Médio:    " << avgEnergy << " Joules/Nó" << std::endl;
    std::cout << "   - Latência Média:   " << avgLatency << " segundos" << std::endl;
    std::cout << "==== RAIO-X DE PERDAS (GATEWAY PHY) ====" << std::endl;
    std::cout << "   - Colisões (Interferência): " << dropsInterference << " pacotes perdidos"
              << std::endl;
    std::cout << "   - Bloqueio (Sinal Fraco):   " << dropsUnderSensitivity << " pacotes perdidos"
              << std::endl;
    std::cout << "==== DISTRIBUIÇÃO FINAL DE DR/SF ====" << std::endl;
    std::cout << "   - SF12 (DR0): " << drCount[0] << " nós | SF11 (DR1): " << drCount[1] << " nós"
              << std::endl;
    std::cout << "   - SF10 (DR2): " << drCount[2] << " nós | SF9  (DR3): " << drCount[3] << " nós"
              << std::endl;
    std::cout << "   - SF8  (DR4): " << drCount[4] << " nós | SF7  (DR5): " << drCount[5] << " nós"
              << std::endl;
    std::cout << "=======================================================\n" << std::endl;

    // Output para o script .sh ler (Adicionados novos campos no final)
    std::cout << "[RES]," << scenario << "," << nNodes << "," << totalConsumed << "," << avgEnergy
              << "," << globalPdr << "," << jainIndex << "," << execTimeSecs << "," << avgLatency
              << "," << dropsInterference << "," << dropsUnderSensitivity << "," << drCount[0]
              << "," << drCount[1] << "," << drCount[2] << "," << drCount[3] << "," << drCount[4]
              << "," << drCount[5] << std::endl;

    Simulator::Destroy();
    return 0;
}