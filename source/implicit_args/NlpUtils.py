class NlpUtils:
	def __init__(self):
		pass

	def current_to_root(self,index, ptree):
		leaf=ptree
		path=ptree.leaf_treeposition(index)
		for ind in path[0:(len(path)-1)]:
			leaf=leaf[ind]
		label=''
		for ind in path[0:(len(path)-1)]:
			label=leaf.parent().label()+'_'+label
			leaf=leaf.parent()

		return label