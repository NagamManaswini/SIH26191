import React, { useEffect, useState } from "react";
import { Sidebar, navItems } from "./components/Sidebar";
import { Header } from "./components/Header";
import { OfflineBanner } from "./components/OfflineBanner";
import { LoginPage, UserAuth } from "./pages/LoginPage";
import { UserDashboard } from "./pages/UserDashboard";
import { OverviewDashboard } from "./pages/OverviewDashboard";
import { LiveHazardMap } from "./pages/LiveHazardMap";
import { RedZoneAnalysis } from "./pages/RedZoneAnalysis";
import { PopulationMetricsPage } from "./pages/PopulationMetricsPage";
import { SheltersPage } from "./pages/SheltersPage";
import { CarryingCapacityPage } from "./pages/CarryingCapacityPage";
import { EvacuationPlanningPage } from "./pages/EvacuationPlanningPage";
import { RelocationPlanPage } from "./pages/RelocationPlanPage";
import { AnimalSafetyPage } from "./pages/AnimalSafetyPage";
import { CommunityCommunicationPage } from "./pages/CommunityCommunicationPage";
import { AIAssistantPage } from "./pages/AIAssistantPage";
import { AlertsPage } from "./pages/AlertsPage";
import { SystemHealthPage } from "./pages/SystemHealthPage";
import { OfflineEmergencyPage } from "./pages/OfflineEmergencyPage";
import { HospitalsPage } from "./pages/HospitalsPage";
import { HospitalDashboard } from "./pages/HospitalDashboard";
import { HospitalProfilePage } from "./pages/HospitalProfilePage";
import { HospitalCapacityPage } from "./pages/HospitalCapacityPage";
import { HospitalEmergencyPage } from "./pages/HospitalEmergencyPage";
import { HospitalPatientsPage } from "./pages/HospitalPatientsPage";
import { HospitalAmbulancesPage } from "./pages/HospitalAmbulancesPage";
import { api } from "./api/apiClient";

export const App: React.FC = () => {
  const [user, setUser] = useState<UserAuth | null>(() => {
    const saved = localStorage.getItem("disaster_app_user");
    return saved ? JSON.parse(saved) : null;
  });

  const [activeTab, setActiveTab] = useState<string>(() => {
    // Restore correct default tab based on persisted role
    const saved = localStorage.getItem("disaster_app_user");
    if (saved) {
      try {
        const u = JSON.parse(saved);
        if (u.role === "hospital") return "hospital-dashboard";
        if (u.role === "user") return "user-portal";
      } catch (e) {}
    }
    return "overview";
  });
  const [isOffline, setIsOffline] = useState<boolean>(!navigator.onLine);

  // Global Active Location State - Synced across ALL modules
  const [currentLocation, setCurrentLocation] = useState<{ name: string; lat: number; lon: number }>(() => {
    const saved = localStorage.getItem("disaster_app_location");
    return saved
      ? JSON.parse(saved)
      : { name: "Chennai, Tamil Nadu", lat: 13.0827, lon: 80.2707 };
  });

  const handleLocationChange = (loc: { name: string; lat: number; lon: number; weather?: any }) => {
    const newLoc = { name: loc.name, lat: loc.lat, lon: loc.lon };
    setCurrentLocation(newLoc);
    localStorage.setItem("disaster_app_location", JSON.stringify(newLoc));
  };

  const handleLogin = (authUser: UserAuth) => {
    setUser(authUser);
    localStorage.setItem("disaster_app_user", JSON.stringify(authUser));
    if (authUser.role === "user") {
      setActiveTab("user-portal");
    } else if (authUser.role === "hospital") {
      setActiveTab("hospital-dashboard");
    } else {
      setActiveTab("overview");
    }
  };

  const handleLogout = () => {
    setUser(null);
    localStorage.removeItem("disaster_app_user");
  };

  useEffect(() => {
    const handleOnline = () => {
      setIsOffline(false);
      api.getShelters().catch(() => {});
      api.getHazards().catch(() => {});
    };

    const handleOffline = () => {
      setIsOffline(true);
    };

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  // If user is not logged in, render Login Page
  if (!user) {
    return <LoginPage onLogin={handleLogin} />;
  }

  const currentItem = navItems.find((item) => item.id === activeTab) || navItems[0];

  const renderActivePage = () => {
    // Security: hospital role can ONLY access hospital pages or shared pages (map, communication)
    if (user.role === "hospital") {
      switch (activeTab) {
        case "hospital-dashboard": return <HospitalDashboard user={user} onNavigate={(tab) => setActiveTab(tab)} />;
        case "hospital-profile": return <HospitalProfilePage user={user} />;
        case "hospital-capacity": return <HospitalCapacityPage user={user} />;
        case "hospital-emergency": return <HospitalEmergencyPage user={user} />;
        case "hospital-patients": return <HospitalPatientsPage user={user} />;
        case "hospital-ambulances": return <HospitalAmbulancesPage user={user} />;
        case "hospital-alerts": return <AlertsPage currentLocation={currentLocation} />;
        case "hospital-assignments":
          return (
            <div className="p-8 text-center">
              <HospitalsPage user={user} currentLocation={currentLocation} />
            </div>
          );
        case "map":
          return (
            <LiveHazardMap
              currentLocation={currentLocation}
              onLocationChange={handleLocationChange}
              onNavigate={(tab) => setActiveTab(tab)}
            />
          );
        case "communication": return <CommunityCommunicationPage user={user} currentLocation={currentLocation} />;
        case "hospital-settings":
          return <HospitalProfilePage user={user} />;
        default:
          return <HospitalDashboard user={user} onNavigate={(tab) => setActiveTab(tab)} />;
      }
    }

    switch (activeTab) {
      case "user-portal":
        return <UserDashboard onNavigate={(tab) => setActiveTab(tab)} />;
      case "overview":
        return <OverviewDashboard onNavigate={(tab) => setActiveTab(tab)} />;
      case "map":
        return (
          <LiveHazardMap
            currentLocation={currentLocation}
            onLocationChange={handleLocationChange}
            onNavigate={(tab) => setActiveTab(tab)}
          />
        );
      case "red-zone":
        return (
          <RedZoneAnalysis
            user={user}
            currentLocation={currentLocation}
            onLocationChange={handleLocationChange}
            onNavigate={(tab) => setActiveTab(tab)}
          />
        );
      case "population":
        return (
          <PopulationMetricsPage
            currentLocation={currentLocation}
            onLocationChange={handleLocationChange}
            onNavigate={(tab) => setActiveTab(tab)}
          />
        );
      case "shelters":
        return <SheltersPage currentLocation={currentLocation} />;
      case "hospitals":
        return <HospitalsPage user={user} currentLocation={currentLocation} />;
      case "capacity":
        return <CarryingCapacityPage currentLocation={currentLocation} />;
      case "evacuation":
        return <EvacuationPlanningPage />;
      case "relocation":
        return <RelocationPlanPage />;
      case "animal-safety":
        return <AnimalSafetyPage user={user} />;
      case "communication":
        return <CommunityCommunicationPage user={user} currentLocation={currentLocation} />;
      case "ai-assistant":
        return <AIAssistantPage />;
      case "alerts":
        return <AlertsPage currentLocation={currentLocation} />;
      case "offline":
        return <OfflineEmergencyPage />;
      case "health":
        return <SystemHealthPage />;
      default:
        return user.role === "user" ? (
          <UserDashboard onNavigate={(tab) => setActiveTab(tab)} />
        ) : (
          <OverviewDashboard onNavigate={(tab) => setActiveTab(tab)} />
        );
    }
  };

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-50 text-slate-900 font-sans">
      {/* Navigation Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isOffline={isOffline}
        user={user}
        onLogout={handleLogout}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-full overflow-y-auto">
        <Header activeTabLabel={currentItem.label} user={user} onLogout={handleLogout} currentLocation={currentLocation} />
        <OfflineBanner isOffline={isOffline} onSync={() => api.getShelters().then(() => setIsOffline(false)).catch(() => {})} />
        <main className="flex-1">{renderActivePage()}</main>
      </div>
    </div>
  );
};

export default App;
