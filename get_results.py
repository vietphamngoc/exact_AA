from code.stats.get_stats import parallel_stats

for n in range(4,9):
	for k in range(2, n):
		parallel_stats(n, 16, 25, f"junta_{k}")


