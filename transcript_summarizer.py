from TranscriptSummarizerAI import TranscriptSummarizer  # Assuming you saved the script as transcript_summarizer.py

# Initialize the summarizer
summarizer = TranscriptSummarizer()

# Define your CSV data as a string with proper formatting
csv_data = """transcript_id,speaker,timestamp,message
T7,Zoe,00:00:10,Meeting initiated with agenda.
T7,Adam,00:15:00,Budget approved for Q1.
T7,Zoe,00:30:00,Discussed next steps for project.
T7,Eve,00:45:00,Status update on ongoing tasks.
T7,Adam,01:05:00,Action items have been assigned.
T8,Brian,01:00:00,Project kickoff and overview.
T8,Cathy,01:20:00,We have decided to extend the deadline.
T8,Brian,01:40:00,Scope approved by management.
T8,Diana,02:00:00,Action items finalized for deliverables.
T8,Cathy,02:10:00,Review meeting schedule and next steps."""

# Process the data
report = summarizer.process_transcript_data(csv_data, "csv")
print(report)