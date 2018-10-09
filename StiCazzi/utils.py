import json, decimal, hashlib

def decimal_dumps(d):
	def fix_dict(d):
		fixed = {}
		for k,v in d.items():
			if isinstance(v, decimal.Decimal):
				# convert decimal to string
				fixed.update({k: str(v)})
			elif isinstance(v, dict):
				# recurse
				fixed.update({k: fix_dict(v)})
			else:
				# no conversion needed, replace
				fixed.update({k: v})
		return fixed
	return json.dumps(fix_dict(d))


def safe_file_name(name, type):
	
	name = str(name).encode('utf-8')
	type = str(type)
	ext = "xxx"
	
	try:
		ext = type.split("/")[1]
	except:
		ext = "xxx"
		
	final_fname = hashlib.sha1(name).hexdigest()
	final_fname += "." + ext

	return final_fname
