


def detector_filter(res):
	ret = []
	for entry in res:
		i,score,cl = entry
		if score>0.5:
			ret.append (entry)
	return ret
