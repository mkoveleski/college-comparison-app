import requests
import json
import ttkbootstrap as ttk
from tkinter import ttk as tk_tt
from tkinter import StringVar, Frame, Label, Entry, Button, Text, END
from modules import api

class CollegeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("College Comparison App")

        self.search_var = StringVar()
        self.setup_ui()

    def setup_ui(self):
        search_frame = Frame(self.root)
        search_frame.pack(pady=10)

        Label(search_frame, text="Enter College Name:").pack(side="left")
        Entry(search_frame, textvariable=self.search_var).pack(side="left", padx=5)
        Button(search_frame, text="Search", command=self.search_college).pack(side="left")

        self.tabs = tk_tt.Notebook(self.root)
        self.overview_tab = Frame(self.tabs)
        self.demographics_tab = Frame(self.tabs)
        self.location_tab = Frame(self.tabs)

        self.tabs.add(self.overview_tab, text="Overview")
        self.tabs.add(self.demographics_tab, text="Demographics")
        self.tabs.add(self.location_tab, text="Location Snapshot")

        self.tabs.pack(expand=1, fill="both")

        self.overview_content = Label(self.overview_tab, justify="left", anchor="nw")
        self.overview_content.pack(padx=10, pady=10, anchor="nw")

        self.demographics_content = Label(self.demographics_tab, justify="left", anchor="nw")
        self.demographics_content.pack(padx=10, pady=10, anchor="nw")

        self.location_content = Label(self.location_tab, justify="left", anchor="nw")
        self.location_content.pack(padx=10, pady=10, anchor="nw")

    def search_college(self):
        college_name = self.search_var.get()
        if not college_name.strip():
            return

        self.overview_content.config(text="Loading data...")
        self.demographics_content.config(text="")
        self.location_content.config(text="")

        try:
            data = api.search_college(college_name)
            if not data:
                self.overview_content.config(text="No results found.")
                return

            # Overview tab
            school_name = data.get("school.name", "Unknown")
            school_city = data.get("school.city", "Unknown")
            school_state = data.get("school.state", "Unknown")
            school_id = data.get("id", "N/A")
            school_url = data.get("school.school_url", "N/A")
            ownership = data.get("school.ownership_label", "N/A")
            degree = data.get("school.degrees_awarded.highest_label", "N/A")
            carnegie = data.get("school.carnegie_basic_label", "N/A")
            grad = data.get("latest.completion.completion_rate_4yr_150nt", "N/A")
            ret_ft = data.get("latest.completion.retention_rate.four_year.full_time", "N/A")
            ret_pt = data.get("latest.completion.retention_rate.four_year.part_time", "N/A")
            enrollment = data.get("latest.student.size", "N/A")

            self.overview_content.config(text=(
                f"{school_name} ({school_city}, {school_state})\n"
                f"School ID: {school_id}\n"
                f"Website: {school_url}\n"
                f"Ownership: {ownership}\n"
                f"Highest Degree: {degree}\n"
                f"Carnegie Class: {carnegie}\n"
                f"Enrollment: {enrollment}\n"
                f"Graduation Rate: {grad}\n"
                f"Retention Rate (FT): {ret_ft}\n"
                f"Retention Rate (PT): {ret_pt}"
            ))

            # Demographics tab
            white = data.get("latest.student.demographics.race_ethnicity.white", "N/A")
            black = data.get("latest.student.demographics.race_ethnicity.black", "N/A")
            hispanic = data.get("latest.student.demographics.race_ethnicity.hispanic", "N/A")
            asian = data.get("latest.student.demographics.race_ethnicity.asian", "N/A")
            female = data.get("latest.student.demographics.female_share", "N/A")
            male = data.get("latest.student.demographics.men", "N/A")
            first_gen = data.get("latest.student.share_firstgeneration", "N/A")
            pell = data.get("latest.student.share_pell", "N/A")

            self.demographics_content.config(text=(
                f"White: {white}\n"
                f"Black: {black}\n"
                f"Hispanic: {hispanic}\n"
                f"Asian: {asian}\n"
                f"Female: {female}\n"
                f"Male: {male}\n"
                f"First-Gen: {first_gen}\n"
                f"Pell Grant Recipients: {pell}"
            ))

            # Location tab
            location_data = api.get_location_snapshot(data)
            if location_data:
                self.location_content.config(text=(
                    f"Population: {location_data['population']}\n"
                    f"Median Income: ${location_data['median_income']}\n"
                    f"Poverty Rate: {location_data['poverty_rate']}%"
                ))
            else:
                self.location_content.config(text="Location data not available.")

        except Exception as e:
            self.overview_content.config(text=f"Error: {str(e)}")
