from code.stats.get_stats import run_stats

for n in [4,6,8]:
	for k_0 in [0,1,2,3,4]:
		run_stats(n, 16, 50, k_0=k_0, step=2)




