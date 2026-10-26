namespace MulakatSim.Domain;

public enum InterviewStatus
{
    Created,
    Active,
    Paused,
    Completed,
    Reported,
    Failed,
    Deleted,
}

public enum InterviewMode
{
    Text,
    Voice,
}

public enum CandidateLevel
{
    Intern,
    Junior,
    Mid,
    Senior,
}

public enum Speaker
{
    Interviewer,
    Candidate,
}

public enum DocumentKind
{
    Cv,
    JobPosting,
}

public enum UsageKind
{
    Llm,
    Stt,
    Tts,
}
