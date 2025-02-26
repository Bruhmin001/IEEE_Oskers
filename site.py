import streamlit as st
import pandas as pd
import pickle
import os
import numpy as np

def load_pkl(filename):
    if os.path.exists(filename):
        with open(filename, 'rb') as f:
            return pickle.load(f)
    return None

def calculate_seasonal_average(df, district):
    df.columns = df.columns.str.strip()
    df_district = df[df['Dist Name'].str.strip() == district]

    if df_district.empty:
        st.error(f"No data found for district: {district}")
        return pd.DataFrame()

    required_columns = {
        'Summer': ['MARCH MAXIMUM (Centigrate)', 'APRIL MAXIMUM (Centigrate)', 'MAY MAXIMUM (Centigrate)'],
        'Monsoon': ['JUNE MAXIMUM (Centigrate)', 'JULY MAXIMUM (Centigrate)', 'AUGUST MAXIMUM (Centigrate)', 'SEPTEMBER MAXIMUM (Centigrate)'],
        'Winter': ['OCTOBER MAXIMUM (Centigrate)', 'NOVEMBER MAXIMUM (Centigrate)', 'DECEMBER MAXIMUM (Centigrate)', 'JANUARY MAXIMUM (Centigrate)', 'FEBRUARY MAXIMUM (Centigrate)']
    }

    seasonal_data = {}

    for season, cols in required_columns.items():
        available_cols = [col for col in cols if col in df_district.columns]
        
        if not available_cols:
            seasonal_data[season] = np.nan
            continue

        df_district[available_cols] = df_district[available_cols].apply(pd.to_numeric, errors='coerce')
        df_district[available_cols] = df_district[available_cols].fillna(df_district[available_cols].mean())

        seasonal_data[season] = df_district[available_cols].mean(axis=1).values

    return pd.DataFrame(seasonal_data, index=df_district.index)

def main():
    st.title("District-wise Crop Yield Prediction")
    
    file_path = 'combined_data.csv'
    if not os.path.exists(file_path):
        st.error("Dataset not found!")
        return
    
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        return
    
    if 'Dist Name' not in df.columns:
        st.error("Error: No 'Dist Name' column found in dataset!")
        return
    
    districts = sorted(df['Dist Name'].unique())
    selected_district = st.selectbox("Select a district:", districts)
    
    if selected_district:
        model_filename = f"models/{selected_district}_sarimax_model.pkl"
        
        model = load_pkl(model_filename)
        if model is not None:
            try:
                seasonal_avg = calculate_seasonal_average(df, selected_district)
                
                if seasonal_avg.empty:
                    st.error("No seasonal data available for the selected district!")
                    return
                
                adjusted_seasonal_data = {}
                
                for col in seasonal_avg.columns:
                    col_data = seasonal_avg[col].dropna()
                    if len(col_data) > 0:
                        col_min = float(col_data.min())
                        col_max = float(col_data.max())
                        col_mean = float(col_data.mean())
                        adjusted_value = st.slider(f"{col}", min_value=col_min, max_value=col_max, value=col_mean)
                        adjusted_seasonal_data[col] = adjusted_value
                    else:
                        adjusted_seasonal_data[col] = 0.0
                
                exog_data = pd.DataFrame([adjusted_seasonal_data] * 5)
                
                try:
                    if hasattr(model, 'exog_names') and model.exog_names is not None:
                        if set(exog_data.columns) != set(model.exog_names):
                            st.error(f"Exogenous variable mismatch! Model expects: {model.exog_names}")
                            return
                    predictions = model.forecast(steps=5, exog=exog_data)
                    pred_df = pd.DataFrame(predictions)
                    st.dataframe(pred_df)
                except Exception as e:
                    st.error(f"Prediction error: {e}")
            except Exception as e:
                st.error(f"Error calculating seasonal averages: {e}")
        else:
            st.error(f"Prediction model not found for {selected_district}!")

if __name__ == "__main__":
    main()
