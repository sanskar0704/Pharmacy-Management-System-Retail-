// Frontend logic for Pharmacy Management System

let billItems = [];

function formatCurrency(value) {
	return '₹' + Number(value).toFixed(2);
}

async function fetchAndDisplaySummary() {
	try {
		const res = await fetch('/api/summary');
		const json = await res.json();
		if (!json.success) return;
		const d = json.data || {};
		document.querySelector('#kpi-total-medicines').textContent = d.total_medicines ?? 0;
		document.querySelector('#kpi-total-units').textContent = d.total_units ?? 0;
		document.querySelector('#kpi-low-stock').textContent = d.low_stock ?? 0;
		document.querySelector('#kpi-sales-today').textContent = formatCurrency(d.sales_today ?? 0);
	} catch (e) {
		/* silent fail for dashboard */
	}
}


// --- Modern medicine search for billing page ---
let medicinesList = [];
let selectedMedicine = null;

async function fetchMedicines() {
	const res = await fetch('/api/medicines');
	const json = await res.json();
	if (json.success) medicinesList = json.data || [];
}

function showMedicineSuggestions(query) {
	const suggestions = document.getElementById('medicine-suggestions');
	if (!suggestions) return;
	suggestions.innerHTML = '';
	let matches = medicinesList;
	if (query) {
		matches = medicinesList.filter(m => m.name.toLowerCase().includes(query.toLowerCase()));
	}
	matches.forEach(med => {
		const div = document.createElement('div');
		div.className = 'suggestion-item';
		div.innerHTML = `
			<span>${med.name} (${med.manufacturer})</span>
			<input type="number" min="1" value="1" style="width:60px;margin-left:8px;" id="qty-suggest-${med.id}">
			<button class="btn primary" style="margin-left:8px;" id="add-suggest-${med.id}">Add</button>
		`;
		suggestions.appendChild(div);
		div.querySelector(`#add-suggest-${med.id}`).onclick = () => {
			const qty = Number(div.querySelector(`#qty-suggest-${med.id}`).value) || 1;
			addMedicineToBillFromSuggestion(med, qty);
		};
	});
}

function addMedicineToBillFromSuggestion(med, qty) {
	if (!med) return;
	const existing = billItems.find(i => i.medicine_id === med.id);
	if (existing) {
		existing.quantity += qty;
	} else {
		billItems.push({
			medicine_id: med.id,
			name: med.name,
			price: med.price,
			quantity: qty
		});
	}
	renderBill();
	document.getElementById('medicine-suggestions').innerHTML = '';
	document.getElementById('medicine_search').value = '';
	selectedMedicine = null;
}

// Removed unused functions - medicine selection now handled directly in suggestions

function renderBill() {
	const tbody = document.querySelector('#current-bill tbody');
	tbody.innerHTML = '';
	let grand = 0;
	billItems.forEach(item => {
		const lineTotal = item.quantity * Number(item.price);
		grand += lineTotal;
		const tr = document.createElement('tr');
		tr.innerHTML = `
			<td>${item.name}</td>
			<td>
				<button class="btn" onclick="changeBillQuantity(${item.medicine_id},-1)">-</button>
				<span class="tag">${item.quantity}</span>
				<button class="btn" onclick="changeBillQuantity(${item.medicine_id},1)">+</button>
			</td>
			<td>${formatCurrency(item.price)}</td>
			<td>${formatCurrency(lineTotal)}</td>
			<td><button class="btn" onclick="removeBillItem(${item.medicine_id})">Remove</button></td>
		`;
		tbody.appendChild(tr);
	});
	document.getElementById('grand-total').textContent = formatCurrency(grand);
}

window.removeBillItem = function(id) {
	billItems = billItems.filter(i => i.medicine_id !== id);
	renderBill();
}

window.changeBillQuantity = function(id, delta) {
	const item = billItems.find(i => i.medicine_id === id);
	if (!item) return;
	item.quantity += delta;
	if (item.quantity <= 0) {
		window.removeBillItem(id);
	} else {
		renderBill();
	}
}

document.addEventListener('DOMContentLoaded', async () => {
	const searchInput = document.getElementById('medicine_search');
	if (searchInput) {
		await fetchMedicines();
		searchInput.addEventListener('input', e => {
			showMedicineSuggestions(e.target.value);
		});
		searchInput.addEventListener('focus', e => {
			showMedicineSuggestions(searchInput.value);
		});
	}
});


async function handleAddMedicineSubmit(event) {
	event.preventDefault();
	const form = event.currentTarget;
	const formData = new FormData(form);
	const payload = Object.fromEntries(formData.entries());
	payload.quantity = Number(payload.quantity || 0);
	payload.price = Number(payload.price || 0);

	try {
		const res = await fetch('/api/medicines/add', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(payload),
		});
		const json = await res.json();
		if (!json.success) throw new Error(json.message || 'Failed to add');
		form.reset();
		await fetchMedicines();
		await fetchAndDisplaySummary();
		alert('Medicine added successfully');
	} catch (err) {
		alert('Error adding medicine: ' + err.message);
	}
}

function openEditMedicine(id) {
	const med = inventory.find((m) => m.id === id);
	if (!med) return;
	const name = prompt('Name', med.name);
	if (name === null) return;
	const manufacturer = prompt('Manufacturer', med.manufacturer || '') ?? '';
	const batch_no = prompt('Batch No', med.batch_no || '') ?? '';
	const expiry_date = prompt('Expiry Date (YYYY-MM-DD)', med.expiry_date || '') ?? '';
	const quantity = Number(prompt('Quantity', med.quantity) ?? med.quantity);
	const price = Number(prompt('Price', med.price) ?? med.price);
	updateMedicine({ id, name, manufacturer, batch_no, expiry_date, quantity, price });
}

async function updateMedicine(m) {
	try {
		const res = await fetch(`/api/medicines/${m.id}`, {
			method: 'PUT',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(m),
		});
		const json = await res.json();
		if (!json.success) throw new Error(json.message || 'Update failed');
		await fetchMedicines();
		alert('Medicine updated');
	} catch (e) {
		alert('Error updating: ' + e.message);
	}
}

async function deleteMedicine(id) {
	if (!confirm('Delete this medicine?')) return;
	try {
		const res = await fetch(`/api/medicines/${id}`, { method: 'DELETE' });
		const json = await res.json();
		if (!json.success) throw new Error(json.message || 'Delete failed');
		await fetchMedicines();
		alert('Medicine deleted');
	} catch (e) {
		alert('Error deleting: ' + e.message);
	}
}

async function finalizeSale() {
	if (billItems.length === 0) {
		alert('No items in bill');
		return;
	}
	const customer_name = document.querySelector('#customer_name').value.trim();
	const payload = {
		customer_name,
		items: billItems.map((i) => ({ medicine_id: i.medicine_id, quantity: i.quantity, price: i.price })),
	};
	try {
		const res = await fetch('/api/sales/create', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(payload),
		});
        const json = await res.json();
        if (!json.success) throw new Error(json.message || 'Sale failed');
        const saleId = json.sale_id;
        billItems = [];
        renderBill();
        await fetchMedicines();
        await fetchAndDisplaySummary();
        // Redirect to Sales page with a print trigger for the new sale
        window.location.href = `/static/sales.html#print=${saleId}`;
	} catch (err) {
		alert('Error finalizing sale: ' + err.message);
	}
}

// Lightweight print template for the latest sale
function buildBillHtml(header, items) {
    const rows = items.map(i => `
        <tr>
            <td>${i.medicine_name}</td>
            <td style="text-align:right;">${i.quantity_sold}</td>
            <td style="text-align:right;">₹${Number(i.price_per_item).toFixed(2)}</td>
            <td style="text-align:right;">₹${Number(i.line_total).toFixed(2)}</td>
        </tr>
    `).join('');
    return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Bill #${header.id}</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; }
    .title { text-align:center; font-size:18px; font-weight:700; margin-bottom:4px; }
    .sub { text-align:center; font-size:12px; color:#555; margin-bottom:16px; }
    table { width:100%; border-collapse:collapse; }
    th, td { border:1px solid #ddd; padding:6px; font-size:12px; }
    th { background:#f5f5f5; text-align:left; }
    .right { text-align:right; }
    .footer { margin-top:16px; font-size:12px; text-align:center; color:#666; }
    @media print { button { display:none; } }
  </style>
  </head>
  <body>
    <div class="title">Pharmacy Management System</div>
    <div class="sub">Bill #${header.id} • ${new Date(header.sale_date).toLocaleString()} • ${header.customer_name || 'Walk-in Customer'}</div>
    <table>
      <thead>
        <tr>
          <th>Item</th>
          <th class="right">Qty</th>
          <th class="right">Price</th>
          <th class="right">Total</th>
        </tr>
      </thead>
      <tbody>
        ${rows}
      </tbody>
      <tfoot>
        <tr>
          <td colspan="3" class="right"><strong>Grand Total</strong></td>
          <td class="right"><strong>₹${Number(header.total_amount).toFixed(2)}</strong></td>
        </tr>
      </tfoot>
    </table>
    <div class="footer">Thank you for your purchase!</div>
    <button onclick="window.print()">Print</button>
  </body>
  </html>`;
}

async function onPrintBill() {
    const btn = document.getElementById('print-bill');
    if (!btn || !btn.dataset.saleId) return;
    const saleId = btn.dataset.saleId;
    try {
        const res = await fetch(`/api/sales/${saleId}`);
        const json = await res.json();
        if (!json.success) throw new Error(json.message || 'Failed to load sale');
        const { header, items } = json.data;
        const html = buildBillHtml(header, items);
        const w = window.open('', '_blank');
        if (!w) return alert('Popup blocked. Please allow popups to print.');
        w.document.open();
        w.document.write(html);
        w.document.close();
        // auto print
        w.onload = () => w.print();
    } catch (e) {
        alert('Unable to print bill: ' + e.message);
    }
}

// Attach print handler on pages that have the button
document.addEventListener('DOMContentLoaded', () => {});

async function generateReport() {
	try {
		const res = await fetch('/api/sales');
		const json = await res.json();
		if (!json.success) throw new Error(json.message || 'Failed to get sales');
		renderSalesList(json.data || []);
	} catch (err) {
		alert('Error loading sales: ' + err.message);
	}
}

function renderSalesList(rows) {
	const table = document.querySelector('#sales-table');
	if (!table) return;
	const tbody = table.querySelector('tbody');
	tbody.innerHTML = '';
	rows.forEach((r) => {
		const tr = document.createElement('tr');
		tr.innerHTML = `
			<td>${r.id}</td>
			<td>${r.customer_name || ''}</td>
			<td>${r.sale_date}</td>
			<td class="right">$${formatCurrency(r.total_amount)}</td>
			<td><button class="btn" data-view-sale="${r.id}">View</button></td>
		`;
		tbody.appendChild(tr);
	});

	document.querySelectorAll('[data-view-sale]').forEach((btn)=>{
		btn.addEventListener('click', ()=> viewSaleDetails(btn.getAttribute('data-view-sale')));
	});
}

async function viewSaleDetails(id) {
	try {
		const res = await fetch(`/api/sales/${id}`);
		const json = await res.json();
		if (!json.success) throw new Error(json.message || 'Failed to load sale');
		const d = json.data;
		const container = document.querySelector('#sale-details');
		if (!container) return;
		const lines = d.items.map(i=>`<tr><td>${i.medicine_name}</td><td class=\"right\">${i.quantity_sold}</td><td class=\"right\">$${formatCurrency(i.price_per_item)}</td><td class=\"right\">$${formatCurrency(i.line_total)}</td></tr>`).join('');
		container.innerHTML = `
			<div class="tag">Sale #${d.header.id} - ${d.header.customer_name || ''} - ${d.header.sale_date}</div>
			<table class="table">
				<thead><tr><th>Item</th><th class=\"right\">Qty</th><th class=\"right\">Price</th><th class=\"right\">Total</th></tr></thead>
				<tbody>${lines}</tbody>
				<tfoot><tr><td colspan=\"3\" class=\"right\">Grand Total</td><td class=\"right\">$${formatCurrency(d.header.total_amount)}</td></tr></tfoot>
			</table>
		`;
	} catch (e) {
		alert('Error: ' + e.message);
	}
}

async function checkSessionOrRedirect() {
	try {
		const res = await fetch('/api/check_session');
		const json = await res.json();
		if (!json.logged_in) {
			window.location.href = '/static/login.html';
			return false;
		}
		return true;
	} catch {
		window.location.href = '/static/login.html';
		return false;
	}
}

async function logout() {
	try {
		await fetch('/api/logout');
	} finally {
		window.location.href = '/static/login.html';
	}
}

document.addEventListener('DOMContentLoaded', async () => {
	const ok = await checkSessionOrRedirect();
	if (!ok) return;

	// Attach logout if present
	const logoutBtn = document.querySelector('#logout');
	if (logoutBtn) logoutBtn.addEventListener('click', logout);

	// Load inventory table if present
	if (document.querySelector('#inventory-table')) {
		await fetchMedicines();
	}

	// Wire add medicine form if present
	const addForm = document.querySelector('#add-medicine-form');
	if (addForm) addForm.addEventListener('submit', handleAddMedicineSubmit);

	// Wire billing if present
	const finalizeBtn = document.querySelector('#finalize-sale');
	if (finalizeBtn) finalizeBtn.addEventListener('click', finalizeSale);

	// Wire sales list if present
	if (document.querySelector('#sales-table')) {
		await generateReport();
	}
});


