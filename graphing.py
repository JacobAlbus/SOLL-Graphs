import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
import os
pd.options.mode.chained_assignment = None  # default="warn"


class SurveyGraphing:

    def __init__(self, survey_df, greek_emails, american_emails,
                 email_question_number, is_post_course=False):

        self.greek_emails = greek_emails
        self.american_emails = american_emails
        self.survey_df = survey_df

        self.greek_indexes, self.american_indexes = self.create_indices(email_question_number)

        # creates file paths
        survey_questions_file_path = "survey-questions/"
        if is_post_course:
            survey_questions_file_path += "post_course/"
            self.graph_file_path = "graphs/post-course/"
        else:
            survey_questions_file_path += "pre_course/"
            self.graph_file_path = "graphs/pre-course/"

        qualitative_single_file = open(survey_questions_file_path + "qualitative_single.csv", "r")
        self.qualitative_single = qualitative_single_file.read().split("\n")
        qualitative_single_file.close()

        qualitative_multi_file = open(survey_questions_file_path + "qualitative_multi.csv", "r")
        self.qualitative_multi = qualitative_multi_file.read().split("\n")
        qualitative_multi_file.close()

        qualitative_text_file = open(survey_questions_file_path + "qualitative_text.csv", "r")
        self.qualitative_text = qualitative_text_file.read().split("\n")
        qualitative_text_file.close()

        # creates file path for graphs if it doesn't exist
        if not os.path.exists(self.graph_file_path):
            os.makedirs(self.graph_file_path)

    def create_indices(self, email_question_number):
        greek_indexes = []
        american_indexes = []

        for index in range(self.survey_df[email_question_number].shape[0]):
            if self.survey_df[email_question_number].iloc[index] in self.greek_emails:
                greek_indexes.append(index)
            elif self.survey_df[email_question_number].iloc[index] in self.american_emails:
                american_indexes.append(index)

        return greek_indexes, american_indexes

    def format_title(self, title, max_length=9):
        words = title.split(" ")
        new_title = ""
        if len(words) > max_length:
            for index in range(len(words)):
                new_title += words[index] + " "
                if index > 0 and index % max_length == 0:
                    new_title += "\n"
            return new_title
        else:
            return title

    def graph_surveys(self):
        for feature in self.qualitative_multi:
            self.graph_multi_choice(feature)
        for feature in self.qualitative_single:
            self.graph_single_choice(feature)

    """
    functions for graphing single answer questions onto pie charts
    """
    def graph_single_choice(self, feature):
        print(feature)
        title = self.survey_df[feature].iloc[0]

        greek_unique_answers, greek_frequencies_dict = \
            self.find_unique_answers(feature, self.greek_indexes)
        american_unique_answers, american_frequencies_dict = \
            self.find_unique_answers(feature, self.american_indexes)

        # orders the answers and frequencies between the two sets, this is to
        # make sure the coloring for each answer is the same between the two sets
        ordered_greek_answers, ordered_american_answers = self.order_answers(greek_unique_answers, american_unique_answers)
        greek_answer_frequencies = self.order_frequencies_dict(ordered_greek_answers, greek_frequencies_dict)
        american_answer_frequencies = self.order_frequencies_dict(ordered_american_answers, american_frequencies_dict)

        # plots ans saves the pie charts
        color_dict = self.create_label_color_dict(greek_unique_answers, american_unique_answers)
        self.draw_pie_chart(ordered_american_answers, american_answer_frequencies,
                            ordered_greek_answers, greek_answer_frequencies,
                            color_dict, feature, title)

    def find_unique_answers(self, feature, indexes):
        answers = self.survey_df[feature].iloc[indexes].tolist()

        index = 0
        # cleans answers and adds text response if "Other" was selected
        while index < len(answers):
            if not isinstance(answers[index], str):
                answers.remove(answers[index])
                continue
            elif "other" in str.lower(answers[index]):
                for nib in self.qualitative_text:
                    if feature + "_" in nib and isinstance(self.survey_df[nib].iloc[index + 2], str):
                        answers[index] = self.survey_df[nib].iloc[index + 2]
                        break
                    answers[index] = "Other"

            index += 1

        unique_answers = []
        answer_count_dict = {}
        for answer in answers:
            if answer not in unique_answers:
                unique_answers.append(answer)
                answer_count_dict[answer] = answers.count(answer)

        return unique_answers, answer_count_dict

    def order_answers(self, greek_unique_answers, american_unique_answers):
        all_unique_answers = list(set(greek_unique_answers) | set(american_unique_answers))
        ordered_greek_answers = []
        ordered_american_answers = []

        for answer in all_unique_answers:
            if answer in greek_unique_answers and answer in american_unique_answers:
                ordered_greek_answers.append(answer)
                ordered_american_answers.append(answer)

        for answer in all_unique_answers:
            if answer in greek_unique_answers and answer not in ordered_greek_answers:
                ordered_greek_answers.append(answer)
            if answer in american_unique_answers and answer not in ordered_american_answers:
                ordered_american_answers.append(answer)

        return ordered_greek_answers, ordered_american_answers

    def order_frequencies_dict(self, ordered_answers, frequencies_dict):
        answer_frequencies = []
        for answer in ordered_answers:
            answer_frequencies.append(frequencies_dict[answer])

        return answer_frequencies

    def draw_pie_chart(self, american_answers, american_frequencies,
                       greek_answers, greek_frequencies,
                       color_dict, feature, title):

        fig, axs = plt.subplots(2, figsize=(16, 8))
        fig.suptitle(title)

        axs[0].title.set_text("American")
        american_pie_wedge_collection = axs[0].pie(american_frequencies, labels=american_answers,
                                                   autopct=self.autopct_format(american_frequencies))
        for pie_wedge in american_pie_wedge_collection[0]:
            pie_wedge.set_edgecolor('white')
            pie_wedge.set_facecolor(color_dict[pie_wedge.get_label()])

        axs[1].title.set_text("Greek")
        greek_pie_wedge_collection = axs[1].pie(greek_frequencies, labels=greek_answers,
                                                autopct=self.autopct_format(greek_frequencies))
        for pie_wedge in greek_pie_wedge_collection[0]:
            pie_wedge.set_edgecolor('white')
            pie_wedge.set_facecolor(color_dict[pie_wedge.get_label()])

        plt.savefig(self.graph_file_path + feature + ".png")
        plt.clf()

    def create_label_color_dict(self, greek_unique_answers, american_unique_answers):
        available_colors = ["tab:blue", "tab:red", "tab:green", "tab:orange",
                            "tab:cyan", "tab:purple", "tab:olive", "tab:pink",
                            "tab:brown", "goldenrod", "indigo"]

        label_color_dict = {}
        all_unique_answers = []

        for answer in american_unique_answers:
            if answer not in all_unique_answers:
                all_unique_answers.append(answer)
        for answer in greek_unique_answers:
            if answer not in all_unique_answers:
                all_unique_answers.append(answer)

        for answer in all_unique_answers:
            color = available_colors[0]
            label_color_dict[answer] = color
            available_colors.pop(0)

        return label_color_dict

    def autopct_format(self, values):
        def my_format(pct):
            total = sum(values)
            val = int(round(pct*total/100.0))
            return '{v:d}'.format(v=val)
        return my_format

    """
    functions for graphing multiple answer questions onto bar graphs
    """
    def graph_multi_choice(self, feature):
        print(feature)
        title = self.survey_df[feature].iloc[0]

        # aggregates multiple choice answers for each group of students
        greek_unique_answers, greek_answer_frequencies = \
            self.aggregate_multiple_choice_answers(feature, self.greek_indexes)
        american_unique_answers, american_answer_frequencies = \
            self.aggregate_multiple_choice_answers(feature, self.american_indexes)

        fig, axs = plt.subplots(2, figsize=(16, 8))
        fig.suptitle(title)

        # graphs each bar chart independently
        axs[0].title.set_text("Greek")
        axs[0].bar(greek_unique_answers, greek_answer_frequencies)
        try:
            axs[0].set_yticks(np.arange(max(greek_answer_frequencies) + 1))
        except ValueError:
            pass

        axs[1].title.set_text("American")
        axs[1].bar(american_unique_answers, american_answer_frequencies)
        try:
            axs[1].set_yticks(np.arange(max(american_answer_frequencies) + 1))
        except ValueError:
            pass

        plt.savefig(self.graph_file_path + feature + ".png")
        plt.clf()

    def aggregate_multiple_choice_answers(self, feature, indexes):
        answers = self.survey_df[feature].iloc[indexes]

        total_answers = []
        for answer in answers:
            if isinstance(answer, str):
                answer = re.sub(r"\([^()]*\)", "", answer)  # removes parentheses
                for item in answer.split(","):
                    total_answers.append(self.format_title(item, 1))

        unique_answers = []
        answer_count = []
        for answer in total_answers:
            if answer not in unique_answers:
                unique_answers.append(answer.split("(")[0])
                answer_count.append(total_answers.count(answer))

        return unique_answers, answer_count

    """
    functions for graphing proficiency scatter plots
    """
    def graph_proficiencies(self, prof_test_df, email_list, survey_report_target_language_question,
                            survey_email_question, prof_email_question, title):
        reported_proficiency = []
        test_proficiency = []

        for email in email_list:
            prof_test_index = prof_test_df[prof_email_question].tolist().index(email)
            survey_index = self.survey_df[survey_email_question].tolist().index(email)

            test_proficiency.append(int(prof_test_df["SC0"].iloc[prof_test_index]))

            reported = self.survey_df[survey_report_target_language_question].iloc[survey_index]
            if reported.split()[0] == "A1":
                reported_proficiency.append(1)
            elif reported.split()[0] == "A2":
                reported_proficiency.append(2)
            elif reported.split()[0] == "B1":
                reported_proficiency.append(3)
            elif reported.split()[0] == "B2":
                reported_proficiency.append(4)
            elif reported.split()[0] == "C1":
                reported_proficiency.append(5)
            elif reported.split()[0] == "C2":
                reported_proficiency.append(6)

        self.plot_scatters(reported_proficiency, test_proficiency, title)

    def plot_scatters(self, reported_proficiency, test_proficiency, title):
        plt.title(title)

        plt.xlabel("Reported Proficiency Level")
        plt.xlim(1, 7)
        x_ticks = ["", "A1", "A2", "B1", "B2", "C1", "C2"]
        plt.xticks(range(len(x_ticks)), x_ticks, size='small')

        plt.ylabel("Proficiency Test Score")
        min_score = min(test_proficiency)
        plt.ylim(max(min_score - 2, 0), 30)

        plt.scatter(reported_proficiency, test_proficiency)
        plt.savefig("graphs/" + title + ".png")
        plt.clf()

    """
    Functions for plotting simple binary bar graphs
    """
    def graph_avg_unique_languages(self):
        # counts total number of languages taken by each group
        greek_avg_lang_count = self.calculate_avg_unique_languages(self.greek_indexes, "Q7", "Q7_10_TEXT")
        american_avg_lang_count = self.calculate_avg_unique_languages(self.american_indexes, "Q7", "Q7_10_TEXT")

        title = "Average Number of Unique Languages"
        numbers = [greek_avg_lang_count, american_avg_lang_count]
        self.plot_bar_graph(title, numbers)

    def calculate_avg_unique_languages(self, group_indexes, survey_language_question, text_question):
        language_count = 0
        for index in self.greek_indexes:
            langauges = self.survey_df[survey_language_question].iloc[index]
            for language in langauges.split(","):
                if "other" not in str.lower(language):
                    language_count += 1
                else:
                    other_languages = self.survey_df["Q7_10_TEXT"].iloc[index].split(",")
                    language_count += len(other_languages)

        return language_count / len(group_indexes)

    def graph_reported_average_prof_levels(self, language_proficiency_questions):
        american_reported_prof_levels = self.calculate_reported_average_prof_levels(language_proficiency_questions,
                                                                                    self.american_indexes)
        greek_reported_prof_levels = self.calculate_reported_average_prof_levels(language_proficiency_questions,
                                                                                 self.greek_indexes)

        numbers = [greek_reported_prof_levels, american_reported_prof_levels]
        title = "Average Reported Prof Levels"
        self.plot_bar_graph(title, numbers, is_y_axis_prof_levels=True)

    def calculate_reported_average_prof_levels(self, language_proficiency_questions, group_indexes):
        proficiency_level_frequencies = {"A1": 0, "A2": 0, "B1": 0,
                                         "B2": 0, "C1": 0, "C2": 0}
        total_level = 0
        for question in language_proficiency_questions:
            for index in group_indexes:
                response = self.survey_df[question].iloc[index]
                if isinstance(response, str):
                    if response.split()[0] == "A1":
                        proficiency_level_frequencies["A1"] += 1
                        total_level += 1
                    elif response.split()[0] == "A2":
                        proficiency_level_frequencies["A2"] += 1
                        total_level += 2
                    elif response.split()[0] == "B1":
                        proficiency_level_frequencies["B1"] += 1
                        total_level += 3
                    elif response.split()[0] == "B2":
                        proficiency_level_frequencies["B2"] += 1
                        total_level += 4
                    elif response.split()[0] == "C1":
                        proficiency_level_frequencies["C1"] += 1
                        total_level += 5
                    elif response.split()[0] == "C2":
                        proficiency_level_frequencies["C2"] += 1
                        total_level += 6

        avg_unique_language_count = self.calculate_avg_unique_languages(group_indexes, "Q7", "Q7_10_Text")
        return total_level / (len(group_indexes) * avg_unique_language_count)

    def graph_reported_target_prof_levels(self, american_target_langauge_question, greek_target_language_question):
        language_proficiency_questions = [american_target_langauge_question]
        american_reported_prof_levels = self.calculate_reported_average_prof_levels(language_proficiency_questions,
                                                                                    self.american_indexes)

        language_proficiency_questions = [greek_target_language_question]
        greek_reported_prof_levels = self.calculate_reported_average_prof_levels(language_proficiency_questions,
                                                                                 self.greek_indexes)

        numbers = [greek_reported_prof_levels, american_reported_prof_levels]
        title = "Average Reported Target Prof Levels"
        self.plot_bar_graph(title, numbers, is_y_axis_prof_levels=True)

    def plot_bar_graph(self, title, numbers, is_y_axis_prof_levels=False):
        plt.figure(figsize=(10, 6))
        plt.title(title)

        plt.xlabel("Groups")
        plt.ylabel("Avg. Unique Language")

        if is_y_axis_prof_levels:
            plt.ylabel("Proficiency Level")
            plt.ylim(1, 6)
            y_ticks = ["", "A1 (1)", "A2 (2)", "B1 (3)", "B2 (4)", "C1 (5)", "C2 (6)"]
            plt.yticks(range(len(y_ticks)), y_ticks, size='small')
        else:
            plt.ylim(0, max(numbers[0], numbers[1]) * 1.3)

        groups = ["Greeks", "Americans"]

        plt.bar(groups, numbers)
        plt.savefig("graphs/" + title + ".png")
        plt.clf()
