import app


# Test 1: Check if a technical resume gets a valid score between 0 and 100
def test_score_candidate_is_reasonable_for_technical_resume():
    resume_text = "Python, SQL, AWS, 5 years experience in ML and leadership"
    job_description = "Python SQL AWS ML leadership"

    score = app.score_candidate(resume_text, job_description)

    # Score should be a decimal number (float) between 0 and 100
    assert isinstance(score, float)
    assert score > 0
    assert score <= 100


# Test 2: Check if a non-technical (design) resume also gets a valid score
def test_score_candidate_handles_non_technical_resume():
    resume_text = "Visual designer with 6 years in branding, Adobe Illustrator, Figma, portfolio, art direction, and client management"
    job_description = "Visual designer with branding, illustration, portfolio, adobe, figma"

    score = app.score_candidate(resume_text, job_description)

    assert isinstance(score, float)
    assert score > 0
    assert score <= 100


# Test 3: Check that the score breakdown has points for skills, portfolio, and overall
def test_score_candidate_breakdown_for_design_role():
    resume_text = "Creative art director with 7 years of branding, illustration, art direction, portfolio, Adobe Photoshop, Figma, and client management"
    job_description = "Senior visual designer for branding and art direction"

    breakdown = app.score_candidate_breakdown(resume_text, job_description)

    assert breakdown["overall"] > 0
    assert breakdown["portfolio"] > 0
    assert breakdown["skills"] > 0


# Test 4: Check if seniority mode correctly puts the person with more experience first
def test_rank_candidates_uses_seniority_mode():
    resumes = [
        {
            "filename": "junior.pdf",
            "text": "Junior designer with 2 years of experience in branding and illustration"
        },
        {
            "filename": "senior.pdf",
            "text": "Senior design lead with 10 years of experience in branding, art direction, leadership, and client management"
        }
    ]

    job_description = "Senior visual designer"

    ranked = app.rank_candidates(resumes, job_description, rank_mode="seniority")

    # The senior candidate should be #1 in the list
    assert ranked[0]["filename"] == "senior.pdf"
    assert ranked[1]["filename"] == "junior.pdf"


# Test 5: Check if our JSON cleaner correctly handles markdown code blocks
def test_safe_json_load_handles_markdown_block():
    json_with_code_block = "```json\n{\"rankings\": [{\"rank\": 1, \"name\": \"Alice\"}] }\n```"

    parsed = app.safe_json_load(json_with_code_block)

    # Should successfully convert to a Python dictionary
    assert parsed["rankings"][0]["name"] == "Alice"