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
});
