async function submitProfileForm(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const button = form.querySelector('.submit-btn');
    const errorBox = document.getElementById('formError');

    button.disabled = true;
    button.textContent = 'Creating your plan...';
    errorBox.hidden = true;

    const payload = {
        name: form.name.value,
        age: Number(form.age.value),
        weight: Number(form.weight.value),
        fitness_goal: form.fitness_goal.value,
        workout_intensity: form.workout_intensity.value,
        experience_level: form.experience_level.value,
        preferred_workout: form.preferred_workout.value,
        available_time: Number(form.available_time.value),
    };

    try {
        const userResponse = await fetch('/api/users', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });
        const userData = await userResponse.json();
        if (!userResponse.ok) {
            throw new Error(userData.detail || 'Something went wrong while creating your profile.');
        }
        const planResponse = await fetch('/api/workouts/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userData.id }),
        });
        const planData = await planResponse.json();
        if (!planResponse.ok) {
            throw new Error(planData.detail || 'Plan generation failed.');
        }
        window.location.href = `/dashboard/${userData.id}`;
    } catch (error) {
        errorBox.textContent = error.message;
        errorBox.hidden = false;
    } finally {
        button.disabled = false;
        button.textContent = 'Generate My Plan';
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('profileForm');
    if (form) {
        form.addEventListener('submit', submitProfileForm);
    }

    const copyPlanBtn = document.getElementById('copyPlanBtn');
    if (copyPlanBtn) {
        copyPlanBtn.addEventListener('click', async () => {
            const summaryText = document.getElementById('planSummaryText');
            if (!summaryText) return;

            const text = summaryText.textContent.trim();
            try {
                await navigator.clipboard.writeText(text);
                const originalText = copyPlanBtn.textContent;
                copyPlanBtn.textContent = 'Copied!';
                setTimeout(() => {
                    copyPlanBtn.textContent = originalText;
                }, 1200);
            } catch (error) {
                const fallback = document.createElement('textarea');
                fallback.value = text;
                document.body.appendChild(fallback);
                fallback.select();
                document.execCommand('copy');
                document.body.removeChild(fallback);
                copyPlanBtn.textContent = 'Copied!';
                setTimeout(() => {
                    copyPlanBtn.textContent = 'Copy summary';
                }, 1200);
            }
        });
    }

    const refineBtn = document.getElementById('refinePlanBtn');
    if (refineBtn) {
        refineBtn.addEventListener('click', async () => {
            const feedback = document.getElementById('feedbackInput').value.trim();
            const status = document.getElementById('refineStatus');
            if (!feedback) {
                status.textContent = 'Please add feedback before refining.';
                status.hidden = false;
                return;
            }
            status.hidden = false;
            status.textContent = 'FitBuddy AI is refining your plan...';
            refineBtn.disabled = true;
            try {
                const response = await fetch('/api/workouts/refine', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: window.userId, feedback }),
                });
                const data = await response.json();
                if (!response.ok) {
                    throw new Error(data.detail || 'Unable to refine the plan.');
                }
                status.textContent = 'Your plan has been updated successfully.';
                window.location.reload();
            } catch (error) {
                status.textContent = error.message;
            } finally {
                refineBtn.disabled = false;
            }
        });
    }

    const tipBtn = document.getElementById('tipBtn');
    if (tipBtn) {
        tipBtn.addEventListener('click', async () => {
            const result = document.getElementById('tipResult');
            tipBtn.disabled = true;
            tipBtn.textContent = 'Generating...';
            try {
                const response = await fetch('/api/tips/nutrition', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: window.userId }),
                });
                const data = await response.json();
                if (!response.ok) {
                    throw new Error(data.detail || 'Unable to generate a nutrition tip.');
                }
                result.textContent = data.tip;
            } catch (error) {
                result.textContent = error.message;
            } finally {
                tipBtn.disabled = false;
                tipBtn.textContent = 'Generate Tip';
            }
        });
    }

    const habitStorageKey = `fitbuddy-habits-${window.userId || 'guest'}`;
    const habitInputs = document.querySelectorAll('[data-habit]');
    const habitProgressText = document.getElementById('habitProgressText');
    const habitProgressBar = document.getElementById('habitProgressBar');

    function syncHabitProgress() {
        const saved = JSON.parse(localStorage.getItem(habitStorageKey) || '{}');
        let checkedCount = 0;

        habitInputs.forEach((input) => {
            const habitKey = input.dataset.habit;
            const isChecked = Boolean(saved[habitKey]);
            input.checked = isChecked;
            if (isChecked) checkedCount += 1;
        });

        const total = habitInputs.length || 1;
        const percentage = (checkedCount / total) * 100;
        if (habitProgressText) habitProgressText.textContent = `${checkedCount}/${total} done`;
        if (habitProgressBar) habitProgressBar.style.width = `${percentage}%`;
    }

    habitInputs.forEach((input) => {
        input.addEventListener('change', () => {
            const saved = JSON.parse(localStorage.getItem(habitStorageKey) || '{}');
            saved[input.dataset.habit] = input.checked;
            localStorage.setItem(habitStorageKey, JSON.stringify(saved));
            syncHabitProgress();
        });
    });

    if (habitInputs.length) {
        syncHabitProgress();
    }
});
