import boto3
from datetime import datetime, timedelta
from dateutil.parser import parse
import json
import requests

def lambda_handler(event, context):
    batch_client = boto3.client('batch', region_name='us-east-2')
    number_of_seconds = 86400 

    # List all job queues
    response = batch_client.describe_job_queues()
    list_of_jobs=[]
# Iterate through the job queues
    for job_queue in response['jobQueues']:
        job_queue_name = job_queue['jobQueueName']
    
    # List running jobs in each job queue
        running_jobs = batch_client.list_jobs(jobQueue=job_queue_name, jobStatus='RUNNABLE')      ## Replace the jobStatus in order to get more states like Running, Starting etc. 
    
        #print(f"Running jobs in '{job_queue_name}':")
    
        for job in running_jobs['jobSummaryList']:
            job_start_time_str = (job['createdAt'])

            # Convert the Unix timestamp to seconds (divide by 1000)
            job_start_time_str = job_start_time_str/1000 

             # Convert the timestamp to a datetime object
            
            dt_object= datetime.utcfromtimestamp(job_start_time_str)
            print(dt_object)
            formatted_datetime = dt_object.strftime('%Y-%m-%d'+'T'+'%H:%M:%S')

            # Parse the job start time string into a datetime object
            job_start_time = formatted_datetime
            print(type(job_start_time))
            current_time = datetime.now().strftime('%Y-%m-%d'+'T'+'%H:%M:%S')
            print(type(current_time))
                
            print("Calculating the elapsed time")
            # Calculate the elapsed time
            elapsed_time = datetime.strptime(current_time, '%Y-%m-%d'+'T'+'%H:%M:%S') - datetime.strptime(job_start_time, '%Y-%m-%d'+'T'+'%H:%M:%S')
            print(f"elspsed time: {elapsed_time}")

            #if elapsed_time > one_day_ago:
            if elapsed_time.total_seconds() > number_of_seconds:
                print(f"Job ID: {job['jobId']}, Job Name: {job['jobName']}, Elapsed Time: {elapsed_time}")
                list_of_jobs.append({job['jobId']:job['jobName']})
    send_slack_alert(list_of_jobs)

def send_slack_alert(list_of_jobs):
    print("Calling slack alert")
    if len(list_of_jobs) == 0:
        print("No jobs runnaable for more than a day")
        return 0
    
    print("sending slack alert")  
    slack_data=f"""
    :red_circle: Batch Monitoring:
    Job ID and Job Name stuck in runnable for more than 24 hours are: {list_of_jobs}
    """
    post = {	"text":"{0}".format(slack_data)	}
    slack_hook = <slack_Hook>
    response = requests.post(slack_hook, data=json.dumps(post),headers={'Content-Type': 'application/json'})
    if response.status_code!=200:
        raise ValueError('Request to slack returned an error %s, the response is:\n%s'
        % (response.status_code, response.text))




