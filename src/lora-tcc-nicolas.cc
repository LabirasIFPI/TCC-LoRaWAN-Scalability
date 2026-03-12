/*
 * Copyright (C) 2025 Nícolas Rafael Silva Alves
 * * Este programa é software livre: podes redistribuí-lo e/ou modificá-lo
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

#include <iostream> // Faltou incluir esta biblioteca para o std::cout
#include "ns3/applications-module.h"
#include "ns3/core-module.h"
#include "ns3/energy-module.h"
#include "ns3/lorawan-module.h"
#include "ns3/mobility-module.h"
#include "ns3/netanim-module.h"
#include "ns3/network-module.h"
#include "ns3/propagation-module.h"
#include "ns3/point-to-point-module.h" // Necessário para o Backhaul P2P

using namespace ns3;
using namespace lorawan;

// --- Variáveis Globais de Controle ---
int nNodes = 100;
double radius = 5000.0;
double simulationTime = 3600.0;
int scenario = 1; // 1 = Estático, 2 = ADR
int appPeriod = 600;

int main(int argc, char *argv[]) {
  // Desativa os logs nativos do NS-3 para limpar o terminal (usaremos nosso próprio painel)
  // LogComponentEnable("TCC_Nicolas_Sim", LOG_LEVEL_INFO);

  CommandLine cmd;
  cmd.AddValue("nNodes", "Número de nós terminais", nNodes);
  cmd.AddValue("scenario", "1=Estático, 2=ADR", scenario);
  cmd.Parse(argc, argv);

  // =========================================================================
  // PAINEL DE LOG DETALHADO (Início da Simulação)
  // =========================================================================
  std::cout << "\n=======================================================" << std::endl;
  std::cout << " INICIANDO SIMULAÇÃO: TCC NÍCOLAS RAFAEL (LoRaWAN)" << std::endl;
  std::cout << "=======================================================" << std::endl;
  std::cout << " Parâmetros da Rodada:" << std::endl;
  std::cout << "   - Cenário:        " << (scenario == 1 ? "1 (Estático / Anéis Concêntricos)" : "2 (Dinâmico / ADR Ativado)") << std::endl;
  std::cout << "   - Qtd. de Nós:    " << nNodes << " dispositivos" << std::endl;
  std::cout << "   - Tempo Total:    " << simulationTime << " segundos" << std::endl;
  std::cout << "   - Raio da Célula: " << radius << " metros" << std::endl;
  std::cout << "   - Tráfego (App):  1 pacote (51B) a cada " << appPeriod << "s" << std::endl;
  std::cout << "-------------------------------------------------------" << std::endl;
  std::cout << " Simulando... (Pode levar alguns minutos para N elevado)" << std::endl;

  // 1. Criação dos Containers
  NodeContainer endDevices;
  endDevices.Create(nNodes);

  NodeContainer gateways;
  gateways.Create(1);

  // 2. Mobilidade (Simplificada)
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

  // 3. PHY e Configuração de Canal
  Ptr<LogDistancePropagationLossModel> loss = CreateObject<LogDistancePropagationLossModel>();
  loss->SetPathLossExponent(2.9); // Ajuste crítico
  loss->SetReference(1.0, 46.37);

  Ptr<PropagationDelayModel> delay = CreateObject<ConstantSpeedPropagationDelayModel>();
  Ptr<LoraChannel> channel = CreateObject<LoraChannel>(loss, delay);

  LoraPhyHelper phyHelper = LoraPhyHelper();
  phyHelper.SetChannel(channel);

  // 4. MAC e Helpers
  LorawanMacHelper macHelper = LorawanMacHelper();
  macHelper.SetRegion(LorawanMacHelper::EU);

  LoraHelper helper = LoraHelper();
  helper.EnablePacketTracking();

  // Instalação Gateway (PHY + MAC)
  phyHelper.SetDeviceType(LoraPhyHelper::GW);
  macHelper.SetDeviceType(LorawanMacHelper::GW);
  helper.Install(phyHelper, macHelper, gateways);

  // Instalação End Devices (PHY + MAC)
  phyHelper.SetDeviceType(LoraPhyHelper::ED);
  macHelper.SetDeviceType(LorawanMacHelper::ED_A);
  NetDeviceContainer endDevicesNetDevices = helper.Install(phyHelper, macHelper, endDevices);

  // 5. Configuração Individual dos Nós (Evitando ACK Storm)
  for (NodeContainer::Iterator j = endDevices.Begin(); j != endDevices.End(); ++j) {
    Ptr<Node> node = *j;
    Ptr<LoraNetDevice> loraNetDevice = node->GetDevice(0)->GetObject<LoraNetDevice>();
    Ptr<ClassAEndDeviceLorawanMac> mac = loraNetDevice->GetMac()->GetObject<ClassAEndDeviceLorawanMac>();

    if (scenario == 2) {
      // Cenário Dinâmico: ADR Ligado
      mac->SetDataRate(0); // SF12 inicial
      mac->SetMType(LorawanMacHeader::UNCONFIRMED_DATA_UP); // Correção: Sem ACKs
    } else {
      // Cenário Estático
      mac->SetMType(LorawanMacHeader::UNCONFIRMED_DATA_UP);

      Ptr<MobilityModel> mm = node->GetObject<MobilityModel>();
      double distance = mm->GetDistanceFrom(gateways.Get(0)->GetObject<MobilityModel>());

      int dr = 0; // Padrão: DR0 (SF12)
      if (distance < 1330) dr = 5;      // SF7
      else if (distance < 1690) dr = 4; // SF8
      else if (distance < 2150) dr = 3; // SF9
      else if (distance < 2720) dr = 2; // SF10
      else if (distance < 3320) dr = 1; // SF11

      mac->SetDataRate(dr);
      mac->SetTransmissionPowerDbm(14);
    }
  }

  // 5.1 Arquitetura de Rede: Network Server e P2P Backhaul
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
  
  if (scenario == 2) {
    nsHelper.EnableAdr(true);
  } else {
    nsHelper.EnableAdr(false);
  }
  
  nsHelper.Install(networkServer.Get(0));

  // 6. Aplicação
  PeriodicSenderHelper appHelper;
  appHelper.SetPeriod(Seconds(appPeriod));
  appHelper.SetPacketSize(51);
  ApplicationContainer appContainer = appHelper.Install(endDevices);

  Ptr<UniformRandomVariable> x = CreateObject<UniformRandomVariable>();
  x->SetAttribute("Min", DoubleValue(0.0));
  x->SetAttribute("Max", DoubleValue(appPeriod));
  appContainer.StartWithJitter(Seconds(0), x);

  // 7. Energia (Nomenclatura oficial do NS-3 corrigida)
  BasicEnergySourceHelper basicSourceHelper;
  basicSourceHelper.Set("BasicEnergySourceInitialEnergyJ", DoubleValue(10000.0));
  basicSourceHelper.Set("BasicEnergySupplyVoltageV", DoubleValue(3.3));

  LoraRadioEnergyModelHelper radioEnergyHelper;
  radioEnergyHelper.Set("TxCurrentA", DoubleValue(0.028));
  radioEnergyHelper.Set("RxCurrentA", DoubleValue(0.0112));
  radioEnergyHelper.Set("StandbyCurrentA", DoubleValue(0.0014));
  radioEnergyHelper.Set("SleepCurrentA", DoubleValue(0.0000015));

  EnergySourceContainer sources = basicSourceHelper.Install(endDevices);
  DeviceEnergyModelContainer deviceModels = radioEnergyHelper.Install(endDevicesNetDevices, sources);

  // 8. Execução
  Simulator::Stop(Seconds(simulationTime));
  Simulator::Run();

  // 9. Extração de Métricas
  double totalConsumed = 0.0;
  for (uint32_t i = 0; i < endDevices.GetN(); ++i) {
    Ptr<Node> node = endDevices.Get(i);
    Ptr<EnergySourceContainer> sourceContainer = node->GetObject<EnergySourceContainer>();
    if (sourceContainer && sourceContainer->GetN() > 0) {
      Ptr<EnergySource> source = sourceContainer->Get(0);
      double rem = source->GetRemainingEnergy();
      totalConsumed += (10000.0 - rem);
    }
  }
  
  double avgEnergy = (nNodes > 0) ? (totalConsumed / nNodes) : 0.0;
  
  // =========================================================================
  // PAINEL DE LOG DETALHADO (Fim da Simulação)
  // =========================================================================
  std::cout << " Simulação concluída com sucesso!" << std::endl;
  std::cout << " RESULTADOS DE ENERGIA:" << std::endl;
  std::cout << "   - Consumo Total: " << totalConsumed << " Joules" << std::endl;
  std::cout << "   - Consumo Médio: " << avgEnergy << " Joules/Nó" << std::endl;
  std::cout << "=======================================================\n" << std::endl;

  std::cout << "[RES]," << scenario << "," << nNodes << "," << totalConsumed << "," << avgEnergy << std::endl;

  Simulator::Destroy();
  return 0;
}