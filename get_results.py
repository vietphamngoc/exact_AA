from code.stats.get_stats import run_stats

for n in range(9):
	run_stats(n, 16, 50, False)
	for k_0 in range(5):
		run_stats(n, 16, 50, k_0=k_0, step=2)




