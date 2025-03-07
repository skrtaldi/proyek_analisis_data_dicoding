import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import gdown


st.set_page_config(
    page_title="Dashboard Tren Temperatur dan Tekanan Atmosfer",
    layout="wide"
)

file_id = "1GU4-tpp_mqsFNoh3HvBvI2M72lqCSLPF"
url = f"https://drive.google.com/uc?id={file_id}"
output = "data.csv"
gdown.download(url, output, quiet=False)

def load_data():
    data = pd.read_csv(output, parse_dates=["datetime"])
    data["year"] = data["datetime"].dt.year
    data["month"] = data["datetime"].dt.month
    data["day"] = data["datetime"].dt.day
    data["hour"] = data["datetime"].dt.hour
    return data

# Load data
data = load_data()

st.sidebar.header("Filter Data")


min_year, max_year = int(data["year"].min()), int(data["year"].max())
selected_years = st.sidebar.slider("Pilih Rentang Tahun", min_year, max_year, (min_year, max_year))

# Apply filters
filtered_data = data[
    (data["year"] >= selected_years[0]) & 
    (data["year"] <= selected_years[1]) 
]

st.title("Dashboard Tren Temperatur dan Tekanan Atmosfer")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(
        "Rata-Rata Temperatur", 
        f"{filtered_data['TEMP'].mean():.2f} °C",
    )
with col2:
    st.metric(
        "Rata-Rata Tekanan", 
        f"{filtered_data['PRES'].mean():.2f} hPa",
    )
with col3:
    st.metric(
        "Temp. Tertinggi", 
        f"{filtered_data['TEMP'].max():.2f} °C"
    )
with col4:
    st.metric(
        "Temp. Terendah", 
        f"{filtered_data['TEMP'].min():.2f} °C"
    )

st.subheader("Korelasi antara Temperatur dan Tekanan")
corr = filtered_data[['TEMP', 'PRES']].corr().iloc[0, 1]
st.write(f"Koefisien korelasi: {corr:.4f}")

tab1, tab2, tab3 = st.tabs(["Tren Tahunan", "Distribusi", "Analisis Musiman"])

with tab1:
    st.subheader("Tren Tahunan Temperatur dan Tekanan Atmosfer")
    
    yearly_data = filtered_data.groupby("year").agg({
        'TEMP': ['mean', 'min', 'max', 'std'],
        'PRES': ['mean', 'min', 'max', 'std']
    })
    yearly_data.columns = ['TEMP_mean', 'TEMP_min', 'TEMP_max', 'TEMP_std', 
                         'PRES_mean', 'PRES_min', 'PRES_max', 'PRES_std']
    yearly_data = yearly_data.reset_index()
    
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax2 = ax1.twinx()

    ax1.plot(yearly_data['year'], yearly_data['TEMP_mean'], color='red', marker='o', label='Temperature')
    ax1.fill_between(
        yearly_data['year'],
        yearly_data['TEMP_mean'] - yearly_data['TEMP_std'],
        yearly_data['TEMP_mean'] + yearly_data['TEMP_std'],
        color='red', alpha=0.2
    )
    
    ax2.plot(yearly_data['year'], yearly_data['PRES_mean'], color='blue', marker='s', label='Pressure')
    ax2.fill_between(
        yearly_data['year'],
        yearly_data['PRES_mean'] - yearly_data['PRES_std'],
        yearly_data['PRES_mean'] + yearly_data['PRES_std'],
        color='blue', alpha=0.2
    )
    
    ax1.set_xlabel('Tahun', fontsize=12)
    ax1.set_ylabel('Temperature (°C)', color='red', fontsize=12)
    ax2.set_ylabel('Pressure (hPa)', color='blue', fontsize=12)
    
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

    plt.grid(True, alpha=0.3)
    plt.title('Tren Rata-rata Temperatur dan Tekanan Atmosfer Per Tahun', fontsize=14)
    st.pyplot(fig)
    
with tab2:
    st.subheader("Distribusi Temperatur dan Tekanan Atmosfer")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.boxplot(hue="year", y="TEMP", data=filtered_data, ax=ax, palette="RdYlBu_r", legend=False)
        ax.set_title("Distribusi Temperatur Per Tahun")
        ax.set_xlabel("Tahun")
        ax.set_ylabel("Temperature (°C)")
        plt.xticks(rotation=45)
        st.pyplot(fig)
    
    with col2:
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.boxplot(hue="year", y="PRES", data=filtered_data, ax=ax, palette="Blues", legend=False)
        ax.set_title("Distribusi Tekanan Atmosfer Per Tahun")
        ax.set_xlabel("Tahun")
        ax.set_ylabel("Pressure (hPa)")
        plt.xticks(rotation=45)
        st.pyplot(fig)
    
    st.subheader("Histogram dan Density Plot")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.histplot(filtered_data["TEMP"], kde=True, ax=ax, color="red")
        ax.set_title("Distribusi Frekuensi Temperatur")
        ax.set_xlabel("Temperature (°C)")
        st.pyplot(fig)
    
    with col2:
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.histplot(filtered_data["PRES"], kde=True, ax=ax, color="blue")
        ax.set_title("Distribusi Frekuensi Tekanan Atmosfer")
        ax.set_xlabel("Pressure (hPa)")
        st.pyplot(fig)

with tab3:
    st.subheader("Analisis Musiman")
    
    monthly_data = filtered_data.groupby(['year', 'month']).agg({
        'TEMP': 'mean',
        'PRES': 'mean'
    }).reset_index()
    
    month_names = {
        1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'Mei', 6: 'Jun',
        7: 'Jul', 8: 'Agu', 9: 'Sep', 10: 'Okt', 11: 'Nov', 12: 'Des'
    }
    monthly_data['month_name'] = monthly_data['month'].map(month_names)
    
    if len(monthly_data) > 0:
        pivot_temp = pd.pivot_table(
            monthly_data, 
            values='TEMP', 
            index='year', 
            columns='month_name',
            aggfunc='mean'
        )
        
        pivot_pres = pd.pivot_table(
            monthly_data, 
            values='PRES', 
            index='year', 
            columns='month_name',
            aggfunc='mean'
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(pivot_temp, cmap="RdYlBu_r", annot=True, fmt=".1f", linewidths=0.5, ax=ax)
            ax.set_title("Rata-rata Temperatur Bulanan")
            plt.tight_layout()
            st.pyplot(fig)
        
        with col2:
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.heatmap(pivot_pres, cmap="Blues", annot=True, fmt=".1f", linewidths=0.5, ax=ax)
            ax.set_title("Rata-rata Tekanan Atmosfer Bulanan")
            plt.tight_layout()
            st.pyplot(fig)
        
        monthly_avg = filtered_data.groupby('month').agg({
            'TEMP': 'mean',
            'PRES': 'mean'
        }).reset_index()
        monthly_avg['month_name'] = monthly_avg['month'].map(month_names)
        monthly_avg = monthly_avg.sort_values('month')
        
        fig, ax1 = plt.subplots(figsize=(12, 6))
        ax2 = ax1.twinx()
        
        ax1.plot(monthly_avg['month_name'], monthly_avg['TEMP'], color='red', marker='o', linewidth=2, label='Temperature')
        ax2.plot(monthly_avg['month_name'], monthly_avg['PRES'], color='blue', marker='s', linewidth=2, label='Pressure')
        
        ax1.set_xlabel('Bulan', fontsize=12)
        ax1.set_ylabel('Temperature (°C)', color='red', fontsize=12)
        ax2.set_ylabel('Pressure (hPa)', color='blue', fontsize=12)
        
        # Add combined legend
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
        
        plt.grid(True, alpha=0.3)
        plt.title('Pola Musiman Temperatur dan Tekanan Atmosfer', fontsize=14)
        st.pyplot(fig)
    else:
        st.info("Data tidak cukup untuk analisis musiman. Harap pilih rentang tahun yang lebih lebar.")

with st.expander("Lihat Data"):
    st.dataframe(filtered_data)

    csv = filtered_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download data sebagai CSV",
        data=csv,
        file_name="temperature_pressure_data.csv",
        mime="text/csv",
    )