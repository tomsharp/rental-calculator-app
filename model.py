import numpy_financial as npf

from pydantic import BaseModel, computed_field

class Rental(BaseModel):
  sale_price: int 
  down_payment_percent: float
  mortgage_rate: float
  loan_term_years: int 
  closing_costs: int 
  pmi_rate: float
  property_tax_rate: float
  annual_homeowners_insurance: int
  annual_hoa_fees: int
  upfront_repairs: int
  projected_monthly_rent: int
  vacancy_rate_annual: float
  monthly_maintenance_and_repairs: int
  capex: int
  monthly_management_fees: int
  horizon: int
  annualized_appreciation: float

  @computed_field
  @property
  def down_payment(self) -> float:
    return self.down_payment_percent * self.sale_price / 100 

  @computed_field
  @property
  def mortgage_principal(self) -> float:
    return self.sale_price - self.down_payment
  
  @computed_field
  @property 
  def total_upfront_costs(self) -> float: 
    return self.down_payment + self.closing_costs + self.upfront_repairs

  @computed_field
  @property
  def mortgage_payment(self) -> float:
    return - npf.pmt(
        self.mortgage_rate / 100 / 12, 
        12*self.loan_term_years, 
        self.mortgage_principal
    )

  @computed_field
  @property
  def pmi_payment(self) -> float:
    if self.down_payment_percent >= 20:
      return 0
    return self.mortgage_principal * self.pmi_rate / 100 / 12
  
  @computed_field
  @property
  def property_tax_payment(self) -> float:
    return self.sale_price * self.property_tax_rate / 100 / 12

  @computed_field
  @property
  def homeowners_insurance_payment(self) -> float:
    return self.annual_homeowners_insurance / 12

  @computed_field
  @property
  def hoa_fees_payment(self) -> float:
    return self.annual_hoa_fees / 12

  # modeling 
  @computed_field
  @property
  def vacancy_cost_monthly(self) -> float:
    return (self.vacancy_rate_annual / 100 ) * self.projected_monthly_rent

  @computed_field
  @property 
  def variable_expenses(self) -> float:
    # BiggerPockets: "variable" expenses
    return (
        self.vacancy_cost_monthly + 
        self.monthly_maintenance_and_repairs +
        self.capex + 
        self.monthly_management_fees
    ) 

  @computed_field
  @property
  def monthly_expenses(self) -> float:
    return (
        self.mortgage_payment +
        self.property_tax_payment +  
        self.homeowners_insurance_payment + 
            
        # BiggerPockets -> float: "variable" expenses
        self.variable_expenses +

        # not listed on BiggerPockets?
        self.pmi_payment + 
        self.hoa_fees_payment 
    ) 

  @computed_field
  @property
  def monthly_cashflow(self) -> float:
    return self.projected_monthly_rent - self.monthly_expenses