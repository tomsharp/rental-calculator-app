import plotly.graph_objects as go 
import pandas as pd 


def split_df_into_report_tables(df: pd.DataFrame) -> list[pd.DataFrame]:
    return [

        df[[
            'sale_price', 
            'down_payment_percent', 
            'mortgage_rate',
            'loan_term_years', 
            'closing_costs', 
            'pmi_rate', 
            'property_tax_rate',
            'annual_homeowners_insurance',  
        ]],


        df[[
            'upfront_repairs',
            'down_payment',
            'total_upfront_costs',
        ]],


        df[[
            'mortgage_payment',
            'pmi_payment',
            'property_tax_payment',
            'homeowners_insurance_payment',
            'hoa_fees_payment',
        ]],


        df[[
            'vacancy_rate_annual',
            'vacancy_cost_monthly',
            'monthly_maintenance_and_repairs',
            'capex',
            'monthly_management_fees',
            'variable_expenses',
        ]],

        df[[
            'projected_monthly_rent',
            'monthly_expenses',
            'monthly_cashflow',
        ]],
    ]   

def _handle_row_format(x):
    if any([i in x["Metric"].lower() for i in ["rate", "percent"]]):
        return '{:.2%}'.format(x["Value"] / 100)
    
    if float(x["Value"]) >= 0:
        return '${:,.0f}'.format(x["Value"])

    return '$({:,.0f})'.format(abs(x["Value"]))

def process_report_table(table: pd.DataFrame) -> pd.DataFrame: 
    table = table.T
    table = table.reset_index()
    table.columns = ['Metric', 'Value']
    table['Metric'] = table['Metric'].apply(
        lambda x: x.replace('_', ' ').capitalize()
    )
    table["Value"] = table.apply(lambda x: _handle_row_format(x), axis=1)
    return table