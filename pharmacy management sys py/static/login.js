document.addEventListener('DOMContentLoaded', () => {
	const form = document.querySelector('#login-form');
	const errorBox = document.querySelector('#error');
	const toggleBtn = document.querySelector('#toggle-password');
	const passwordInput = document.querySelector('#password');

	if (toggleBtn) {
		toggleBtn.addEventListener('click', () => {
			const isPw = passwordInput.type === 'password';
			passwordInput.type = isPw ? 'text' : 'password';
			toggleBtn.textContent = isPw ? 'Hide' : 'Show';
			toggleBtn.setAttribute('aria-label', isPw ? 'Hide password' : 'Show password');
		});
	}

	form.addEventListener('submit', async (e) => {
		e.preventDefault();
		errorBox.textContent = '';
		const formData = new FormData(form);
		const payload = Object.fromEntries(formData.entries());
		try {
			const res = await fetch('/api/login', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(payload),
			});
			const json = await res.json();
			if (!res.ok || !json.success) {
				throw new Error(json.message || 'Login failed');
			}
			window.location.href = '/static/index.html';
		} catch (err) {
			errorBox.textContent = err.message;
		}
	});
});


