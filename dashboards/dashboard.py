import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Import or generate data
# If you have real data, replace the functions with data loading mechanisms
from simulation_dataset import generate_training_data, generate_device_data

# Generate sample data
training_data = generate_training_data(rounds=20)
device_data = generate_device_data(devices=10)

# Set up the Streamlit app
st.title("Federated Learning Dashboard")
st.sidebar.title("Navigation")
option = st.sidebar.selectbox("Select a view", ["Training Progress", "Device Statuses", "Insights"])

if option == "Training Progress":
    st.header("Training Progress Over Rounds")

    # Plot Loss
    fig1, ax1 = plt.subplots()
    ax1.plot(training_data['Round'], training_data['Loss'], marker='o')
    ax1.set_title('Loss Over Training Rounds')
    ax1.set_xlabel('Round')
    ax1.set_ylabel('Loss')
    st.pyplot(fig1)

    # Plot Accuracy
    fig2, ax2 = plt.subplots()
    ax2.plot(training_data['Round'], training_data['Accuracy'], color='green', marker='o')
    ax2.set_title('Accuracy Over Training Rounds')
    ax2.set_xlabel('Round')
    ax2.set_ylabel('Accuracy')
    st.pyplot(fig2)

elif option == "Device Statuses":
    st.header("IoT Devices and Edge Servers Status")

    # Display device data
    st.dataframe(device_data)

    # Plot CPU Usage
    fig3, ax3 = plt.subplots()
    device_data.plot.bar(x='Device ID', y='CPU Usage (%)', ax=ax3, color='skyblue')
    ax3.set_title('CPU Usage by Device')
    st.pyplot(fig3)

    # Plot Memory Usage
    fig4, ax4 = plt.subplots()
    device_data.plot.bar(x='Device ID', y='Memory Usage (%)', ax=ax4, color='salmon')
    ax4.set_title('Memory Usage by Device')
    st.pyplot(fig4)

elif option == "Insights":
    st.header("Actionable Insights")

    # Example insight: Devices with high CPU usage
    high_cpu_devices = device_data[device_data['CPU Usage (%)'] > 80]
    if not high_cpu_devices.empty:
        st.subheader("Devices with High CPU Usage (>80%)")
        st.table(high_cpu_devices[['Device ID', 'CPU Usage (%)']])
    else:
        st.write("No devices with high CPU usage.")

    # Example insight: Offline devices
    offline_devices = device_data[device_data['Status'] == 'Offline']
    if not offline_devices.empty:
        st.subheader("Offline Devices")
        st.table(offline_devices['Device ID'])
    else:
        st.write("All devices are online.")

# Add more features as needed