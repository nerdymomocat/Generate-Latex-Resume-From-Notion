import os
import notional
from notional.text import markdown

def str_fix(rich_text_obj_arr):
  final_str = ""
  for segment in rich_text_obj_arr:
    ptext = segment.plain_text
    if segment.annotations.bold:
      ptext = "\textbf{" + ptext + "}"
    if segment.annotations.italic:
      ptext = "\textit{" + ptext + "}"
    if segment.href:
      ptext = "\href{" + segment.href + "}{" + ptext + "}"

    final_str += ptext
  return final_str


auth_tokenD = os.getenv("notion_integration_key")
notionD = notional.connect(auth=auth_tokenD)

query = notionD.databases.query(os.getenv("resume_settings_database_id"))
resume_settings_database = []
resume_settings_database_map = {}
for data in query.execute():
  resume_settings_database_single = {}
  resume_settings_database_single["Name"] = str(data["Name"])
  resume_settings_database_single["Rank"] = int(data["Rank"])
  resume_settings_database_single["Item Format"] = str(data["Item Format"])
  resume_settings_database_single["Section Format"] = str(
    data["Section Format"])
  resume_settings_database_single["Sort By"] = str(data["Sort By"])
  resume_settings_database_single["id"] = str(data.id)
  resume_settings_database_map[str(data.id)] = int(data["Rank"]) - 1
  resume_settings_database_single["Items"] = []
  resume_settings_database.append(resume_settings_database_single)

resume_settings_database = sorted(resume_settings_database,
                                  key=lambda x: x['Rank'])

#print(resume_settings_database)

query = notionD.databases.query(os.getenv("resume_database_id"))
resume_database = []
for data in query.execute():
  resume_database_single = {}
  resume_database_single["NP:Name"] = str(data["Name"])
  resume_database_single["NP:URL"] = str(data["URL"])
  resume_database_single["NP:People"] = str_fix(data["People"].rich_text)
  # properties={'People': RichText(type='rich_text', id='%3DiQi', rich_text=[TextObject(type='text', plain_text='Jack Milton', href='https://jackbox.tv/', annotations=Annotations(bold=False, italic=False, strikethrough=False, underline=False, code=False, color=<FullColor.DEFAULT: 'default'>), text=_NestedData(content='Jack Milton', link=LinkObject(type='url', url='https://jackbox.tv/')))]),
  #print(data)
  resume_database_single["NP:Organization"] = str_fix(
    data["Organization"].rich_text)
  resume_database_single["NP:Time"] = str(data["Time"])
  resume_database_single["NP:Comments"] = str_fix(data["Comments"].rich_text)
  resume_database_single["NP:Status"] = str(data["Status"])
  resume_database_single["NP:Geographic Location"] = str(
    data["Geographic Location"])
  resume_database_single["NP:MEOW| Resume Database Formatting"] = str(
    data["MEOW| Resume Database Formatting"].relation[0].id)
  resume_settings_database[resume_settings_database_map[resume_database_single[
    "NP:MEOW| Resume Database Formatting"]]]["Items"].append(
      resume_database_single)
  resume_database.append(resume_database_single)

#print(resume_settings_database)

final_latex = ""

for section in resume_settings_database:
  text_start = ""
  if section["Name"] != "Name":
    text_start = "\section{" + section["Name"] + "}\n"
  text_end = ""
  if section['Section Format'] != '':
    #print(section['Section Format'])
    sec_formats = section['Section Format'].split('NP:Items')
    text_start += sec_formats[0]
    text_end = sec_formats[1]

  final_latex += "\n\n"
  final_latex += text_start + "\n"

  #print(section["Name"], len(section["Items"]))

  for item in section["Items"]:
    item_str = section["Item Format"]
    for key in item:
      item_str = item_str.replace(key, item[key])
    item_str = item_str.replace("\href{}", "")

    final_latex += item_str + "\n"

  final_latex += text_end

final_latex = final_latex.replace("&", "\&")

with open('resume_generated.tex', 'w') as f:
  f.write(final_latex)
