from jinja2 import FileSystemLoader, Environment
from configparser import ConfigParser  
import os
import pandas as pd
import csv
# Content to be published
content = "Hello, world!"
ROOT_report = 'ROOT_report'
Version = 'Version'
FILE_DIR = 'FILE_DIR'
DURATION = 'DURATION'

def getConfig(tag, item):
    config = ConfigParser() 
    config.read('config.ini') 
    temp_ = config.get(tag, item)
    return temp_

def getDir(root, item):
    ver = getConfig(DURATION, Version)
    dir_=''
    root_ = getConfig(FILE_DIR, root)
    type_ = getConfig(FILE_DIR, item)
    if 'test' in root:
        dir_ = root_+ver+'/'+item+'_test_'+ver+'.'+type_
    else: dir_ = root_+ver+'/'+item+'_'+ver+'.'+type_
    return dir_

class ModelResults:
    """
    Class to store the results of a model run and associated data.
    """
    def __init__(self, elem, filepath):
        """
        :param model_name: Name of model.
        :param filepath: Filepath to results .csv.
        """
        self.elem = elem
        self.filepath = filepath
        self.dataset = os.path.split(filepath)[-1]
    
    def getVal(self, elem, file):
        csv_file = csv.reader(open(file, "r"), delimiter=",")
        try:
            for row in csv_file:
                if elem == row[0]:
                    return row[1]
        except Exception as e: print(e)    

    
# Configure Jinja and ready the template
env = Environment(
    loader=FileSystemLoader(searchpath="template")
)
base_template = env.get_template("report.html")
summary_section_template = env.get_template('summary_section.html')
table_section_template = env.get_template('table_section.html')
def main():
    """
    Entry point for the script.
    Render a template and write it to file.
    :return:
    """
    # Content to be published
    title = "End User Debugging Report"
    r = getConfig(FILE_DIR, ROOT_report)
    ver = getConfig(DURATION, Version)
    report_f = r+ver+'/sumary.csv'  
    m = ModelResults('trigger_real_system', report_f)
    trigger_real_system = m.getVal('trigger_real_system', report_f)
    trigger_sim_system = m.getVal('trigger_sim_system', report_f)
    trigger_match = m.getVal('trigger_match', report_f)
    Rule_real_system = m.getVal('Rule_real_system', report_f)
    Rule_sim_system = m.getVal('Rule_sim_system', report_f)
    Rule_match = m.getVal('Rule_match', report_f)
    sections = list()
    sections.append(summary_section_template.render(
        trigger_real_system = trigger_real_system, 
        trigger_sim_system = trigger_sim_system,  
        trigger_match = trigger_match,
        Rule_real_system = Rule_real_system, 
        Rule_sim_system = Rule_sim_system,  
        Rule_match = Rule_match))

    sections.append(table_section_template.render())

    root = getConfig(FILE_DIR, ROOT_report)
    ver = getConfig(DURATION, Version)
    out = root+ver+'/report.html'
    with open(out, "w") as f:
        f.write(base_template.render(
            title=title,
            sections=sections
        ))


if __name__ == "__main__":
    main()