#!/bin/env python3
import glob, os, sys, json, ast
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import runregistry
from modules.jira_api import JiraAPI

def get_input():
	files = glob.glob("Validations/*.txt")
	files.sort(key=os.path.getmtime)
	return files[0] 

def get_run(run_number):
	run = runregistry.get_run(run_number=int(run_number))
	# print(run['oms_attributes'].keys())
	return run

def get_arguments():
	file="_NewValidation.txt"
	os.system("""sed '/^#.*$/d' "%s" > %s""" %(get_input(), file))
	os.system("""sed -i '/^[[:space:]]*$/d' %s""" %(file))
	
	iFile = open(file, 'r')
	args = dict()
	for line in iFile:
		args[line.split(':')[0].strip()] = ":".join(line.split(':')[1:]).strip()
	args['Labels'] = [v.strip() for v in args['Labels'].split(',')]
	return args

def get_mappings():
	mappings = dict()
	mappings['TargetGT_HLT'] 	 = 'newgt'
	mappings['TargetGT_EXPRESS'] = 'newgt'
	mappings['TargetGT_PROMPT']  = 'newgt'
	mappings['ReferenceGT_HLT']  	= 'gt'
	mappings['ReferenceGT_EXPRESS'] = 'gt'
	mappings['ReferenceGT_PROMPT']  = 'gt'
	mappings['Dataset']			= 'ds'

def build_HLT_workflow(args):
	hlt_dict = dict()
	run_number = args['Run'].split(":")[0].strip("{").strip("'")
	run = get_run(run_number)
	oms = run['oms_attributes']

	if args['HLT_release'] == 'None':
		hlt_dict['HLT_release'] = run['oms_attributes']['cmssw_version']
		hlt_dict['PR_release'] = run['oms_attributes']['cmssw_version']
	options = hlt_dict['options'] = dict()
	if round(oms['b_field'])==0:
		options['B0T'] = ""
	if run['class']=="Cosmics21CRUZET":
		options['cosmics'] = ""
	options['HLT'] 			 = "Custom"
	options['Type'] 		 = "HLT+RECO"
	options['HLTCustomMenu'] = "ofcoff:"+oms['hlt_key']
	options['ds']			 = args['Dataset']
	options['basegt']		 = args['ReferenceGT_PROMPT']
	options['gt']			 = args['ReferenceGT_HLT']
	options['newgt']		 = args['TargetGT_HLT']
	options['runLs']		 = ast.literal_eval(args['Run'])
	options['jira']		 	 = args['Jira']
	return hlt_dict

def build_Express_workflow(args):
	express_dict = dict()
	run_number = args['Run'].split(":")[0].strip("{").strip("'")
	run = get_run(run_number)
	oms = run['oms_attributes']

	if args['HLT_release'] == 'None':
		express_dict['HLT_release'] = run['oms_attributes']['cmssw_version']
		express_dict['PR_release'] = run['oms_attributes']['cmssw_version']
	options = express_dict['options'] = dict()
	if round(oms['b_field'])==0:
		options['B0T'] = ""
	if run['class']=="Cosmics21CRUZET":
		options['cosmics'] = ""
	options['HLT'] 			 = "Custom"
	options['Type'] 		 = "EXPR+RECO"
	options['HLTCustomMenu'] = "ofcoff:"+oms['hlt_key']
	options['ds']			 = args['Dataset']
	options['basegt']		 = args['ReferenceGT_PROMPT']
	options['gt']			 = args['ReferenceGT_EXPRESS']
	options['newgt']		 = args['TargetGT_EXPRESS']
	options['runLs']		 = ast.literal_eval(args['Run'])
	options['jira']		 	 = args['Jira']
	return express_dict

def build_Prompt_workflow(args):
	prompt_dict = dict()
	run_number = args['Run'].split(":")[0].strip("{").strip("'")
	run = get_run(run_number)
	oms = run['oms_attributes']

	if args['PR_release'] == 'None':
		prompt_dict['PR_release'] = run['oms_attributes']['cmssw_version']
	else:
		prompt_dict['PR_release'] = args['PR_release']
	options = prompt_dict['options'] = dict()
	if round(oms['b_field'])==0:
		options['B0T'] = ""
	if run['class']=="Cosmics21CRUZET":
		options['cosmics'] = ""
	options['Type'] 		 = "PR"
	options['ds']			 = args['Dataset']
	options['gt']			 = args['ReferenceGT_PROMPT']
	options['newgt']		 = args['TargetGT_PROMPT']
	options['runLs']		 = ast.literal_eval(args['Run'])
	options['jira']		 	 = str(args['Jira'])
	options['two_WFs']		 = ""
	return prompt_dict

if __name__ == '__main__':
	args  = get_arguments()

	sysArgs = sys.argv
	api = JiraAPI(args, sysArgs[1], sysArgs[2])
	ticket = api.check_duplicate()
	if not ticket: 
		args["Jira"]= int(api.get_key().split('-')[1].strip())+1
	else:
		args["Jira"] = int(ticket.split('-')[1].strip())

	hlt_dict 	 = build_HLT_workflow(args)
	express_dict = build_Express_workflow(args)
	prompt_dict  = build_Prompt_workflow(args)

	for data, wid in zip([hlt_dict, express_dict, prompt_dict], ['HLT', 'Express', 'Prompt']):
		rfile = open("metadata_{}.json".format(wid), 'w')
		json.dump(data, rfile, indent=2)
		rfile.close()
			