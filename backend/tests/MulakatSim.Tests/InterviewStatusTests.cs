using MulakatSim.Domain;

namespace MulakatSim.Tests;

public class InterviewStatusTests
{
    private static readonly DateTimeOffset Now = new(2026, 10, 26, 9, 0, 0, TimeSpan.Zero);

    private static Interview NewInterview() => new()
    {
        PersonaId = "tech-lead-backend",
        PersonaVersion = 1,
        Language = "tr",
        Role = "Backend Developer",
    };

    [Fact]
    public void Created_to_Active_is_valid_and_sets_StartedAt()
    {
        var interview = NewInterview();

        interview.TransitionTo(InterviewStatus.Active, Now);

        Assert.Equal(InterviewStatus.Active, interview.Status);
        Assert.Equal(Now, interview.StartedAt);
    }

    [Fact]
    public void Completed_to_Active_is_invalid()
    {
        var interview = NewInterview();
        interview.TransitionTo(InterviewStatus.Active, Now);
        interview.TransitionTo(InterviewStatus.Completed, Now.AddMinutes(20));

        Assert.False(interview.CanTransitionTo(InterviewStatus.Active));
        Assert.Throws<InvalidOperationException>(() => interview.TransitionTo(InterviewStatus.Active, Now.AddMinutes(21)));
        Assert.Equal(InterviewStatus.Completed, interview.Status);
    }

    [Fact]
    public void Pause_and_resume_keeps_original_StartedAt()
    {
        var interview = NewInterview();
        interview.TransitionTo(InterviewStatus.Active, Now);
        interview.TransitionTo(InterviewStatus.Paused, Now.AddMinutes(5));
        interview.TransitionTo(InterviewStatus.Active, Now.AddMinutes(7));

        Assert.Equal(Now, interview.StartedAt);
    }

    [Fact]
    public void Deleted_is_terminal()
    {
        var interview = NewInterview();
        interview.TransitionTo(InterviewStatus.Deleted, Now);

        foreach (var status in Enum.GetValues<InterviewStatus>())
        {
            Assert.False(interview.CanTransitionTo(status));
        }
    }
}
