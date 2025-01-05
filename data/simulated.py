import random
import time
import math
from datetime import datetime, timedelta
from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource

# Configuration
OTEL_COLLECTOR_ENDPOINT = "localhost:4317"
SERVICE_NAME = "energy-system-metrics"

# System parameters
BATTERY_CAPACITY = 100.0  # kWh
NOMINAL_VOLTAGE = 400.0   # V
MAX_CURRENT = 250.0       # A
MAX_POWER = 100.0        # kW

class EnergySystemSimulator:
    def __init__(self):
        self.temperature = 25.0  # Starting at 25°C
        self.soc = 0.8          # Starting at 80% charge
        self.time_of_day = 0    # Hours since midnight
        
    def simulate_temperature(self):
        # Daily temperature variation (sinusoidal with noise)
        base_temp = 25 + 5 * math.sin(2 * math.pi * (self.time_of_day - 14) / 24)
        noise = random.uniform(-0.5, 0.5)
        self.temperature = base_temp + noise
        return self.temperature

    def simulate_power_demand(self):
        # Simulate daily power demand pattern
        base_demand = 40 + 30 * math.sin(2 * math.pi * (self.time_of_day - 12) / 24)
        noise = random.uniform(-5, 5)
        return max(0, min(base_demand + noise, MAX_POWER))

    def simulate_soc(self, power):
        # Update state of charge based on power flow
        energy_delta = power * (10/3600)  # Convert 10-second power to energy
        soc_delta = energy_delta / BATTERY_CAPACITY
        self.soc = max(0.0, min(1.0, self.soc - soc_delta))
        return self.soc * 100  # Return as percentage

    def simulate_current(self, power):
        # Calculate current based on power and voltage
        voltage = self.simulate_voltage()
        return (power * 1000) / voltage  # Convert kW to W for calculation

    def simulate_voltage(self):
        # Voltage varies slightly with load and temperature
        temp_effect = (self.temperature - 25) * -0.1
        soc_effect = (self.soc - 0.5) * 5
        noise = random.uniform(-1, 1)
        return NOMINAL_VOLTAGE + temp_effect + soc_effect + noise

    def simulate_forecast(self):
        # Simulate 24-hour energy demand forecast
        forecast = []
        current_hour = self.time_of_day
        for hour in range(24):
            future_hour = (current_hour + hour) % 24
            base = 40 + 30 * math.sin(2 * math.pi * (future_hour - 12) / 24)
            uncertainty = random.uniform(-10, 10)
            forecast.append(max(0, base + uncertainty))
        return forecast

    def update_time(self):
        self.time_of_day = (self.time_of_day + (10/3600)) % 24  # Add 10 seconds

# Set up OpenTelemetry metrics
resource = Resource.create({"service.name": SERVICE_NAME})
reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint=OTEL_COLLECTOR_ENDPOINT, insecure=True)
)
provider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(provider)
meter = metrics.get_meter(__name__)

# Create OpenTelemetry instruments
otel_metrics = {
    'temperature': meter.create_gauge("temperature", description="System temperature", unit="celsius"),
    'power': meter.create_gauge("power_demand", description="Current power demand", unit="kilowatts"),
    'energy': meter.create_gauge("energy_consumption", description="Cumulative energy consumption", unit="kilowatt_hours"),
    'soc': meter.create_gauge("state_of_charge", description="Battery state of charge", unit="percentage"),
    'current': meter.create_gauge("current", description="System current", unit="amperes"),
    'voltage': meter.create_gauge("voltage", description="System voltage", unit="volts")
}

def main():
    simulator = EnergySystemSimulator()
    cumulative_energy = 0
    
    try:
        while True:
            # Simulate all metrics
            temperature = simulator.simulate_temperature()
            power = simulator.simulate_power_demand()
            cumulative_energy += power * (10/3600)  # 10-second energy consumption
            soc = simulator.simulate_soc(power)
            current = simulator.simulate_current(power)
            voltage = simulator.simulate_voltage()
            forecast = simulator.simulate_forecast()
            
            # Update OpenTelemetry metrics
            otel_metrics['temperature'].set(temperature)
            otel_metrics['power'].set(power)
            otel_metrics['energy'].set(cumulative_energy)
            otel_metrics['soc'].set(soc)
            otel_metrics['current'].set(current)
            otel_metrics['voltage'].set(voltage)
            
            print(f"""
Metrics Update:
Temperature: {temperature:.2f}°C
Power Demand: {power:.2f} kW
Energy Consumption: {cumulative_energy:.2f} kWh
State of Charge: {soc:.2f}%
Current: {current:.2f} A
Voltage: {voltage:.2f} V
            """)
            
            simulator.update_time()
            time.sleep(10)
    
    except KeyboardInterrupt:
        print("\nStopping metric collection...")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        provider.shutdown()

if __name__ == "__main__":
    main()