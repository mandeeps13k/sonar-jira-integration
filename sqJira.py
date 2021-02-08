import json
import requests
import subprocess
import sys
from jira import JIRA
import os
import slack
import time
options = {'server' : 'https://naspersclassifieds.atlassian.net'}
jira_username = sys.argv[1]
jira_api_token = sys.argv[2]
sq_project = sys.argv[3]
slack_token = sys.argv[4]


project_name = str(sq_project)
print(project_name)
command_fetch_vulnerabilities = "curl -u token: https://sonarqube -d 'types=VULNERABILITY&componentKeys="+str(project_name)+"&resolved=false&severities=BLOCKER,CRITICAL,MAJOR'"
print(command_fetch_vulnerabilities)
p = subprocess.Popen(command_fetch_vulnerabilities,stdout=subprocess.PIPE,shell=True)
list = p.communicate()[0]
json_list = json.loads(list)
vulnerability_list = json_list["issues"]


for item in vulnerability_list[:]:
			vulnerability_key = item["key"]
			vulnerability_status = item["status"]
			vulnerability_description = item["message"]
			vulnerability_path = item["component"]
			vulnerability_code_line = item["line"]
			vulnerability_author = item["author"]
			vulnerability_sonar_url = "https://sonarqube.horizontals.olx.org/project/issues?id="+project_name+"&open="+str(vulnerability_key)+"&resolved=false&types=VULNERABILITY"
			vulnerability_information = "Summary:"+str(vulnerability_description)+"\nFile Path :"+str(vulnerability_path)+"\nLine:"+str(vulnerability_code_line)+"\nSonar URL:"+str(vulnerability_sonar_url)+"\nAuthor="+str(vulnerability_author)


			client = slack.WebClient(token=slack_token)
			tmp = "labels="+str(vulnerability_key)
			jira = JIRA(options, basic_auth=(jira_username, jira_api_token))
			issues = jira.search_issues(tmp)
			print(issues)
			print(vulnerability_author)
			vulnerable_assignee = vulnerability_author.replace("@olx.com","")
			print(vulnerable_assignee)
			client.chat_postMessage(channel="pan-security-alerts",text=vulnerability_information+str("\n------------------------------------------------------"))

			if len(issues)==0:
				new_issue = jira.create_issue(project='SEC',summary = vulnerability_description, description = vulnerability_information,issuetype={'name':'Security Issue'},labels=[vulnerability_key,'SonarQube-Panamera'])
				print("New Issue Created")
				vulnerable_assign = jira.search_users(vulnerable_assignee)
				if len(vulnerable_assign)==1:
					new_issue.update(assignee={'name': vulnerable_assignee})
					pass
				else :
					pass
					new_issue.update(assignee={'name':'mandeep.kapoor'})
