import re
import json
import csv
import xml.etree.ElementTree as ET
from datetime import datetime
import io

class TranscriptSummarizer:
    def __init__(self):
        self.decision_indicators = ["approved", "decided", "action", "confirmed", "next steps"]
        
    def validate_data(self, data_str, format_type):
        """Validate input data based on format type."""
        if format_type == "csv":
            return self._validate_csv(data_str)
        elif format_type == "json":
            return self._validate_json(data_str)
        elif format_type == "xml":
            return self._validate_xml(data_str)
        elif format_type == "txt":
            return self._validate_txt(data_str)
        else:
            return False, "ERROR: Invalid data format. Please provide data in CSV, JSON, XML, or TXT markdown format."
    
    def _validate_csv(self, csv_str):
        """Validate CSV data."""
        try:
            csv_reader = csv.reader(io.StringIO(csv_str))
            header = next(csv_reader)
            
            # Check header
            expected_headers = ["transcript_id", "speaker", "timestamp", "message"]
            if not all(h.strip() in expected_headers for h in header):
                return False, "ERROR: Invalid CSV header. Expected: transcript_id, speaker, timestamp, message"
            
            records = list(csv_reader)
            validation_report = self._validate_records(records)
            
            return validation_report
        except Exception as e:
            return False, f"ERROR: Invalid CSV format. {str(e)}"
    
    def _validate_json(self, json_str):
        """Validate JSON data."""
        try:
            data = json.loads(json_str)
            if "transcripts" not in data:
                return False, "ERROR: Invalid JSON structure. Expected 'transcripts' key."
            
            records = []
            for i, transcript in enumerate(data["transcripts"]):
                record = [
                    transcript.get("transcript_id", ""),
                    transcript.get("speaker", ""),
                    transcript.get("timestamp", ""),
                    transcript.get("message", "")
                ]
                records.append(record)
            
            validation_report = self._validate_records(records)
            return validation_report
        except Exception as e:
            return False, f"ERROR: Invalid JSON format. {str(e)}"
    
    def _validate_xml(self, xml_str):
        """Validate XML data."""
        try:
            root = ET.fromstring(xml_str)
            if root.tag != "transcripts":
                return False, "ERROR: Invalid XML structure. Expected root tag 'transcripts'."
            
            records = []
            for i, transcript in enumerate(root.findall("transcript")):
                record = [
                    transcript.find("transcript_id").text if transcript.find("transcript_id") is not None else "",
                    transcript.find("speaker").text if transcript.find("speaker") is not None else "",
                    transcript.find("timestamp").text if transcript.find("timestamp") is not None else "",
                    transcript.find("message").text if transcript.find("message") is not None else ""
                ]
                records.append(record)
            
            validation_report = self._validate_records(records)
            return validation_report
        except Exception as e:
            return False, f"ERROR: Invalid XML format. {str(e)}"
    
    def _validate_txt(self, txt_str):
        """Validate TXT data."""
        try:
            lines = txt_str.strip().split("\n")
            header = lines[0].split("|")
            
            # Check header
            expected_headers = ["transcript_id", "speaker", "timestamp", "message"]
            if not all(h.strip() in expected_headers for h in header):
                return False, "ERROR: Invalid TXT header. Expected: transcript_id|speaker|timestamp|message"
            
            records = []
            for i in range(1, len(lines)):
                record = lines[i].split("|")
                records.append(record)
            
            validation_report = self._validate_records(records)
            return validation_report
        except Exception as e:
            return False, f"ERROR: Invalid TXT format. {str(e)}"
    
    def _validate_records(self, records):
        """Validate records for required fields and format."""
        if not records:
            return False, "ERROR: No transcript records found."
        
        missing_fields = []
        invalid_timestamps = []
        empty_messages = []
        
        for i, record in enumerate(records):
            # Check for missing fields
            if len(record) < 4:
                missing_fields.append(f"Record {i+1}: Missing fields (expected 4, got {len(record)})")
                continue
            
            # Check for empty fields
            for j, field in enumerate(["transcript_id", "speaker", "timestamp", "message"]):
                if not record[j]:
                    missing_fields.append(f"Record {i+1}: Missing {field}")
            
            # Check timestamp format
            timestamp = record[2]
            if not re.match(r"^\d{2}:\d{2}:\d{2}$", timestamp):
                invalid_timestamps.append(f"Record {i+1}")
            
            # Check for empty message
            if record[3].strip() == "":
                empty_messages.append(f"Record {i+1}")
        
        # Generate validation report
        if missing_fields or invalid_timestamps or empty_messages:
            error_messages = []
            if missing_fields:
                error_messages.append("ERROR: Missing required field(s): " + ", ".join(missing_fields))
            if invalid_timestamps:
                error_messages.append("ERROR: Invalid timestamp format in record(s): " + ", ".join(invalid_timestamps) + ". Please use HH:MM:SS.")
            if empty_messages:
                error_messages.append("ERROR: Empty message field in record(s): " + ", ".join(empty_messages) + ". Please correct and resubmit.")
            
            return False, "\n".join(error_messages)
        
        # If all validations pass, return the records
        return True, records
    
    def generate_validation_report(self, records):
        """Generate a validation report in markdown format."""
        report = "# Data Validation Report\n"
        report += "## Data Structure Check:\n"
        report += f"- Number of transcripts: {len(records)}\n"
        report += "- Number of fields per record: 4\n\n"
        
        report += "## Required Fields Check:\n"
        report += "- transcript_id: present\n"
        report += "- speaker: present\n"
        report += "- timestamp: valid\n"
        report += "- message: present\n\n"
        
        report += "## Validation Summary:\n"
        report += "Data validation is successful! Would you like to proceed with summarization or provide another dataset?\n"
        
        return report
    
    def timestamp_to_seconds(self, timestamp):
        """Convert timestamp (HH:MM:SS) to seconds."""
        time_obj = datetime.strptime(timestamp, "%H:%M:%S")
        return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second
    
    def count_decision_indicators(self, message):
        """Count occurrences of decision indicators in a message."""
        message = message.lower()
        return any(indicator in message for indicator in self.decision_indicators)
    
    def analyze_transcripts(self, records):
        """Analyze transcripts and generate a detailed report."""
        # Group records by transcript_id
        transcript_groups = {}
        for record in records:
            transcript_id = record[0]
            if transcript_id not in transcript_groups:
                transcript_groups[transcript_id] = []
            transcript_groups[transcript_id].append(record)
        
        # Analyze each transcript
        analysis_results = {}
        for transcript_id, transcript_records in transcript_groups.items():
            # Sort records by timestamp
            transcript_records.sort(key=lambda x: x[2])
            
            # Calculate metrics
            total_messages = len(transcript_records)
            
            # Key Decision Extraction
            decision_count = sum(1 for record in transcript_records if self.count_decision_indicators(record[3]))
            
            # Transcript Duration
            first_timestamp = transcript_records[0][2]
            last_timestamp = transcript_records[-1][2]
            first_seconds = self.timestamp_to_seconds(first_timestamp)
            last_seconds = self.timestamp_to_seconds(last_timestamp)
            duration = last_seconds - first_seconds
            
            # Decision Density
            decision_density = (decision_count / total_messages) * 100 if total_messages > 0 else 0
            
            # Average Message Length
            total_chars = sum(len(record[3].replace(" ", "")) for record in transcript_records)
            avg_message_length = total_chars / total_messages if total_messages > 0 else 0
            
            # Top Speaker Contribution
            speaker_counts = {}
            for record in transcript_records:
                speaker = record[1]
                if speaker not in speaker_counts:
                    speaker_counts[speaker] = 0
                speaker_counts[speaker] += 1
            
            top_speaker = max(speaker_counts.items(), key=lambda x: x[1]) if speaker_counts else ("", 0)
            top_speaker_ratio = (top_speaker[1] / total_messages) * 100 if total_messages > 0 else 0
            
            # Final recommendation
            if decision_density >= 25.00 and duration > 3600:
                recommendation = "Key decision points are well-distributed in a lengthy session. Highlight all decision points for detailed project insights."
                status = "Optimal Session"
            else:
                recommendation = "Review the transcript for additional decision details and consider requesting more detailed meeting notes."
                status = "Needs More Detail"
            
            analysis_results[transcript_id] = {
                "records": transcript_records,
                "decision_count": decision_count,
                "duration": duration,
                "decision_density": decision_density,
                "avg_message_length": avg_message_length,
                "top_speaker": top_speaker[0],
                "top_speaker_count": top_speaker[1],
                "top_speaker_ratio": top_speaker_ratio,
                "recommendation": recommendation,
                "status": status
            }
        
        return analysis_results
    
    def generate_final_report(self, analysis_results):
        """Generate the final report in markdown format."""
        report = "# Transcript Summary Report\n\n"
        report += f"**Total Transcripts Processed:** {len(analysis_results)}\n\n"
        report += "---\n\n"
        report += "## Detailed Analysis per Transcript\n\n"
        
        for transcript_id, analysis in analysis_results.items():
            report += f"### Transcript ID: {transcript_id}\n\n"
            report += "#### Input Data:\n"
            for record in analysis["records"][:3]:  # Show first 3 records as example
                report += f"- \"Transcript ID\": {record[0]}\n"
                report += f"- \"Speaker\": {record[1]}\n"
                report += f"- \"Timestamp\": {record[2]}\n"
                report += f"- \"Message\": {record[3]}\n\n"
            
            if len(analysis["records"]) > 3:
                report += "... (and more records)\n\n"
            
            report += "---\n\n"
            report += "#### Detailed Calculations:\n\n"
            
            # Key Decision Extraction
            report += "1. **Key Decision Extraction:**\n"
            report += " - **Formula:** $$ \\text{Decision Count} = \\text{number of decision indicator occurrences} $$\n"
            report += " - **Steps:** Identify and count key decision indicator words (approved, decided, action, confirmed, next steps).\n"
            report += f" - **Result:** **{analysis['decision_count']}**\n\n"
            
            # Transcript Duration
            report += "2. **Transcript Duration:**\n"
            report += " - **Formula:** $$ \\text{Duration (seconds)} = \\text{last timestamp (in seconds)} - \\text{first timestamp (in seconds)} $$\n"
            report += " - **Steps:** Convert timestamps and subtract.\n"
            report += f" - **Result:** **{analysis['duration']:.2f} seconds**\n\n"
            
            # Decision Density
            report += "3. **Decision Density:**\n"
            report += " - **Formula:** $$ \\text{Decision Density (\\%)} = \\left(\\frac{\\text{Decision Count}}{\\text{Total messages}}\\right) \\times 100 $$\n"
            report += " - **Steps:** Calculate percentage.\n"
            report += f" - **Result:** **{analysis['decision_density']:.2f}%**\n\n"
            
            # Average Message Length
            report += "4. **Average Message Length:**\n"
            report += " - **Formula:** $$ \\text{Average Message Length} = \\frac{\\text{Total characters (excluding spaces)}}{\\text{Total messages}} $$\n"
            report += " - **Steps:** Count the total characters in all messages (excluding spaces) and divide by the number of messages.\n"
            report += f" - **Result:** **{analysis['avg_message_length']:.2f} characters**\n\n"
            
            # Top Speaker Contribution
            report += "5. **Top Speaker Contribution:**\n"
            report += " - **Formula:** $$ \\text{Top Speaker Ratio (\\%)} = \\left(\\frac{\\text{Messages by top speaker}}{\\text{Total messages}}\\right) \\times 100 $$\n"
            report += " - **Steps:** Count messages per speaker, identify the top speaker, and compute the ratio.\n"
            report += f" - **Result:** **{analysis['top_speaker_ratio']:.2f}%**\n\n"
        
        report += "---\n\n"
        report += "## Final Recommendations\n\n"
        
        for transcript_id, analysis in analysis_results.items():
            report += f"### Transcript ID: {transcript_id}\n"
            report += f"- **Recommendation:** {analysis['recommendation']}\n"
            report += f"- **Status:** {analysis['status']}\n\n"
        
        return report
    
    def process_transcript_data(self, data_str, format_type):
        """Process transcript data and generate a report."""
        # Validate data
        is_valid, result = self.validate_data(data_str, format_type)
        
        if not is_valid:
            return result
        
        # Generate validation report
        validation_report = self.generate_validation_report(result)
        
        # Analyze transcripts
        analysis_results = self.analyze_transcripts(result)
        
        # Generate final report
        final_report = self.generate_final_report(analysis_results)
        
        return validation_report + "\n\n" + final_report

# Example usage
def main():
    summarizer = TranscriptSummarizer()
    
    # Example CSV data
    csv_data = """transcript_id,speaker,timestamp,message
T1,Alice,09:00:00,approved the budget.
T2,Bob,09:15:30,decided on the project timeline.
T3,Alice,09:30:45,confirmed the meeting schedule.
T4,Carol,09:45:15,next steps will be outlined soon.
T5,Bob,10:00:00,action required for follow-up."""
    
    # Process the data
    report = summarizer.process_transcript_data(csv_data, "csv")
    print(report)

if __name__ == "__main__":
    main()