influx_write_api.write(bucket=bucket, org=org, record=point)
            print(f"{i}  inserted successfully")
    except Exception as e:
        print(f"Error inserting job {job.get('job_id', 'N/A')}: {e}")

def store_job_steps(influx_write_api, bucket, org, job_steps):
    try:
        step_id = None
        job_id = None
        for step in job_steps:

            step_id =step["number"]
            job_id = step["job_id"]
            step_started_at = to_rfc3339(step["started_at"])
            step_completed_at = to_rfc3339(step["completed_at"])

            point = (
                Point("ci_workflow_steps")
                .tag("repository_name", step["repository_name"])
                .tag("head_branch", step["head_branch"])
                .tag("workflow_name", step["workflow_name"])
                .tag("actor_name",step["actor_name"])
                .tag("run_id",step["run_id"])
                .tag("workflow_status", step["workflow_status"])
                .tag("workflow_conclusion", step["workflow_conclusion"])
                .tag("event",step["event"])
                .tag("job_id", step["job_id"])
                .tag("job_name", step["job_name"])
                .tag("job_status", step["job_status"])
                .tag("job_conclusion", ["job_conclusion"])
                .tag("step_status", step["step_status"])
                .tag("step_conclusion", step["step_conclusion"])
                .tag("step_name",step["step_name"])
                .tag("step_number",step["number"])
                .field("duration", step["duration"])
                .field("run_attempt", step["run_attempt"])
                .field("completed_at",step_completed_at)
                .time(step_started_at,WritePrecision.NS)
                )
            influx_write_api.write(bucket=bucket, org=org, record=point)
            print(f"job {job_id}'s step {step_id} inserted successfully")
    except Exception as e:
        print(f"Error inserting job {step.get('job_id', 'N/A')}: {e}")

def run_influx(start_date, end_date):
    conn = initialize_mysql_connection()

    try:
        client, write_api, bucket, org = initialize_influx_connection()
        workflow_run_attempts = get_workflow_runs(start_date, end_date,conn)
        print("Length-workflows",len(workflow_run_attempts))
        store_workflow_runs(write_api,bucket, org, workflow_run_attempts)
        workflow_job_attempts = get_workflow_jobs(start_date,end_date,conn)
        print("Length-jobs",len(workflow_job_attempts))
        store_workflow_jobs(write_api,bucket, org, workflow_job_attempts)
        steps = get_job_steps(start_date,end_date,conn)
        print("Length-steps", len(steps))
        store_job_steps(write_api,bucket, org, steps)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()
        client.close()
