def build_prompt(resume_text: str, vacancy: str, options: dict) -> str:
    instructions = []

    if options.get("highlightSkills", False):
        instructions.append(
            "Create a clear Technical Skills section and emphasize the skills most relevant to the vacancy."
        )
    else:
        instructions.append(
            "Do not over-emphasize a separate Technical Skills section unless it is naturally justified by the resume."
        )

    if options.get("optimizeATS", False):
        instructions.append(
            "Optimize the resume for ATS by using clear section headings, standard phrasing, and relevant keywords from the vacancy."
        )
    else:
        instructions.append(
            "Do not explicitly optimize for ATS beyond normal professional clarity."
        )

    if options.get("addSummary", False):
        instructions.append(
            "Include a Professional Summary section tailored to the vacancy."
        )
    else:
        instructions.append(
            "Do not include a Professional Summary section."
        )

    if options.get("addTemperature", False):
        instructions.append(
            "Use slightly stronger, more confident wording while remaining truthful and professional."
        )
    else:
        instructions.append(
            "Keep the tone neutral and professional."
        )

    joined_instructions = "\n".join(f"- {item}" for item in instructions)

    return f"""

You are a resume optimization assistant.

Task:
Rewrite and tailor the candidate's resume for the target vacancy.

Core rules:
- Keep the output professional and ATS-friendly when requested.
- Do not invent experience, education, tools, or achievements that are not supported by the original resume.
- Improve wording, structure, and relevance.
- Focus on aligning existing experience with the vacancy.
- Return plain text only.
- Use these sections only if appropriate:
  1. Professional Summary
  2. Technical Skills
  3. Professional Experience
  4. Projects
  5. Education

Specific instructions:
{joined_instructions}

Target Vacancy:
{vacancy}

Original Resume Text:
{resume_text}
""".strip()