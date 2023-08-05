from dotenv import dotenv_values
from compare2019and2022b import compare_two_matlab_ver  
from get_activity_of_project import plot_activity
from get_evolution_distribution import get_evol_distribution
from get_evoSL_sample_metrics import get_sample_metrics
from get_and_plot_cumulative_metric_distribution import plot_cumulative

config = dotenv_values(".EvoSLenv")
evosl_36 = config['EvoSL_36_2019a']
evosl_compare = config['evoSL_2019avs2022b_5sampleProjects']
evosl_plus = config['EvoSL+_v1']
evosl = config['EvoSL_v1']

print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
print("Showing discrepancies in number of element changes between MATLAB versions")
compare_two_matlab_ver(evosl_compare)
print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

#plot_activity(evosl_plus,evoSL_or_evoSLPlus_flag=True,ten_plus_model_commits=False,figTitle="6(a)")
plot_activity(evosl,evoSL_or_evoSLPlus_flag=True,ten_plus_model_commits=False,figTitle="6(b)")
plot_activity(evosl,evoSL_or_evoSLPlus_flag=True,ten_plus_model_commits=True,figTitle="6(c)")
plot_activity(evosl_36,evoSL_or_evoSLPlus_flag=False,ten_plus_model_commits=False,figTitle="6(d)")

print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
print("Table III")
get_evol_distribution(evosl,evosl_plus,evosl_36)
print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
print("Table V")
get_sample_metrics(evosl_36)
print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
print("Plot cumulative")
plot_cumulative(evosl,evosl_plus)
print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
