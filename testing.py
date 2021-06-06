import pandas as pd
from graphing import SurveyGraphing

greek_emails = ["skarnaspiri@gmail.com", "maikomesxi1@yahoo.com", "up1061695@upnet.gr",
                "up1071781@upnet.gr", "ellenkokkini@gmail.com", "elenapetropoulou6@gmail.com",
                "up1061716@upatras.gr", "piperoumariaeleni@gmail.com", "eleftheria0701@gmail.com",
                "artem.karra@gmail.com"]

american_emails = ["mek9@illinois.edu", "vb8@illinois.edu", "cschwa33@illinois.edu", "theodore.johnson@urbanasd116.org",
                   "christinaphilippou15@gmail.com", "heleng4@illinois.edu", "hamblin2@illinois.edu"]

# graphs every question in survey
survey_data_df = pd.read_csv("post_survey.csv")
grapher = SurveyGraphing(survey_data_df,
                         greek_emails,
                         american_emails,
                         email_question_number="Q64",
                         is_post_course=False)  # TODO: change this to True if graphing post_course
grapher.graph_surveys()

# graphs scatter plot of reported proficiency vs tested proficiency (English)
english_prof_test_df = pd.read_csv("pre_english_prof_test.csv")
title = "Greek Students English Proficiency"
grapher.graph_proficiencies(english_prof_test_df,
                            greek_emails,
                            survey_report_target_language_question="Q8_1",
                            survey_email_question="Q64",
                            prof_email_question="Q33",
                            title=title)

# graphs scatter plot of reported proficiency vs tested proficiency (Greek)
greek_prof_test_df = pd.read_csv("pre_greek_prof_test.csv")
title = "American Students Greek Proficiency"
grapher.graph_proficiencies(greek_prof_test_df,
                            american_emails,
                            survey_report_target_language_question="Q8_2",
                            survey_email_question="Q64",
                            prof_email_question="Q1",
                            title=title)

# graphs bar graphs for number of unique classes
grapher.graph_avg_unique_languages()

language_proficiency_questions = ["Q8_1", "Q8_2", "Q8_3", "Q8_4",
                                  "Q8_5", "Q8_6", "Q8_6_TEXT", "Q8_7",
                                  "Q8_7_TEXT", "Q8_8", "Q8_8_TEXT"]
grapher.graph_reported_average_prof_levels(language_proficiency_questions)

grapher.graph_reported_target_prof_levels(american_target_langauge_question="Q8_2",
                                          greek_target_language_question="Q8_1")

