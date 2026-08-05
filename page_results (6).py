"""View 4: Results - Sales Order (BSP header) + Sales Order Rows (line items) tabs.

Sales Order tab: grouped sections (hero title strip, General, Parties & Billing,
Contacts, Dates & References, Description) instead of a flat grid of boxes.
Sales Order Rows tab: taller table (min 520px) so lines are comfortably visible.

Self-contained: the script hooks renderResults() after the main controller
loads, so app.py needs NO changes.
"""


def _dl_row(key: str, label: str) -> str:
    """One label/value row inside a section card."""
    return f"""
        <div class="flex items-start justify-between gap-4 px-4 py-2.5 border-b border-gray-100 last:border-b-0">
          <span class="font-label-sm text-[10px] text-secondary uppercase tracking-wider pt-0.5 shrink-0">{label}</span>
          <span class="text-[13px] font-medium text-on-surface text-right break-words" data-bsp="{key}">-</span>
        </div>"""


def _section(title: str, icon: str, rows: str) -> str:
    """A section card with a dark header strip (matches the app's panels)."""
    return f"""
      <section class="bg-white border border-gray-200 rounded-DEFAULT shadow-sm overflow-hidden flex flex-col">
        <div class="bg-sidebar-dark px-4 py-2 flex items-center gap-2">
          <span class="material-symbols-outlined text-primary text-[16px]">{icon}</span>
          <h3 class="text-[11px] uppercase tracking-wider text-white font-bold" style="font-family:'JetBrains Mono',monospace;">{title}</h3>
        </div>
        <div class="flex flex-col h-[176px] overflow-y-auto custom-scrollbar"
             style="scrollbar-width:thin; scrollbar-color:#c8c6c6 #f3f3f3;">{rows}</div>
      </section>"""


def _sales_order_panel() -> str:
    general = (_dl_row("external_reference_number", "External Reference (Opp ID)")
               + _dl_row("order_date", "Order Date")
               + _dl_row("location_count", "Location Count")
               + _dl_row("device_services", "Device Services"))
    parties = (_dl_row("company_code", "Company Code")
               + _dl_row("bill_to_party", "Bill To Party")
               + _dl_row("ship_to_party", "Ship To Party"))
    contacts = (_dl_row("customer_contact", "Customer Contact")
                + _dl_row("sales_contact", "Sales Contact")
                + _dl_row("account_manager", "Account Manager"))
    dates_refs = (_dl_row("contract_signed_date", "Contract Signed Date")
                  + _dl_row("customer_required_date", "Customer Required Date")
                  + _dl_row("customer_reference", "Customer Reference")
                  + _dl_row("escalation_level_priority", "Escalation Level (Priority)"))

    return f"""
          <!-- Hero strip: title + status chips -->
          <div class="bg-white border border-gray-200 rounded-DEFAULT shadow-sm px-5 py-4 mb-sm relative overflow-hidden">
            <div class="absolute inset-y-0 left-0 w-1 bg-primary"></div>
            <p class="font-label-sm text-[10px] text-secondary uppercase tracking-wider mb-1">Order Title</p>
            <p class="text-[17px] font-bold text-on-surface font-mono leading-snug break-words" data-bsp="order_title">-</p>
            <p class="text-[12px] text-secondary mt-1 break-words" data-bsp="short_description"></p>
            <div class="flex flex-wrap gap-2 mt-3">
              <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-primary/10 text-primary text-[10px] uppercase font-bold tracking-wider">
                <span class="material-symbols-outlined text-[13px]">fiber_new</span>
                Type: <span data-bsp="order_type">-</span>
              </span>
              <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-sidebar-dark text-white text-[10px] uppercase font-bold tracking-wider">
                <span class="material-symbols-outlined text-[13px]">category</span>
                Category: <span data-bsp="order_category">-</span>
              </span>
              <span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-tertiary/10 text-tertiary text-[10px] uppercase font-bold tracking-wider">
                <span class="material-symbols-outlined text-[13px]">flag</span>
                Status: <span data-bsp="status">-</span>
              </span>
            </div>
          </div>

          <!-- Sections grid -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-sm mb-sm">
            {_section("General", "info", general)}
            {_section("Parties &amp; Billing", "account_balance", parties)}
            {_section("Contacts", "contacts", contacts)}
            {_section("Dates &amp; References", "event_note", dates_refs)}
          </div>

          <!-- Description: full width -->
          <section class="bg-white border border-gray-200 rounded-DEFAULT shadow-sm overflow-hidden">
            <div class="bg-sidebar-dark px-4 py-2 flex items-center gap-2">
              <span class="material-symbols-outlined text-primary text-[16px]">description</span>
              <h3 class="text-[11px] uppercase tracking-wider text-white font-bold" style="font-family:'JetBrains Mono',monospace;">Description</h3>
            </div>
            <p class="px-5 py-4 text-[13px] text-on-surface leading-relaxed whitespace-pre-wrap break-words" data-bsp="description">-</p>
          </section>"""


def view() -> str:
    return """
    <div id="view-results" class="bg-background text-on-surface flex-grow" style="display:none; flex-direction:column; min-height:0;">
      <main class="max-w-7xl mx-auto w-full pt-6 px-6 py-6 flex flex-col flex-grow min-h-0">
        <div class="w-full flex-grow flex flex-col min-h-0">
          <div class="mb-md flex justify-between items-end border-b border-outline/10 pb-2">
            <div>
              <nav class="flex items-center gap-1 mb-1 text-secondary">
                <span class="font-label-sm text-[10px] uppercase">Drafts</span>
                <span class="material-symbols-outlined text-[12px]">chevron_right</span>
                <span class="font-label-sm text-[10px] uppercase text-on-surface">Results</span>
              </nav>
              <h1 class="text-[26px] font-bold text-on-surface leading-tight">Results</h1>
              <p class="font-body-md text-[13px] text-secondary mt-0.5" id="results-opp-subtitle">Review and confirm extracted line items for Opportunity ID: None.</p>
              <p class="font-body-md text-[12px] text-secondary mt-0.5 font-mono" id="results-order-title"></p>
            </div>
            <div class="flex items-center gap-4 pb-1">
              <button onclick="showSection('validation')"
                 class="flex items-center gap-1 px-4 py-1.5 bg-white border border-gray-300 text-gray-700 text-[12px] rounded hover:bg-gray-50 transition-colors uppercase tracking-wider shadow-sm"
                 style="font-family:'JetBrains Mono',monospace;">
                <span class="material-symbols-outlined text-[16px] mr-1">checklist</span> View Validation
              </button>
              <button onclick="exportExcel()"
                 class="flex items-center gap-1 px-4 py-1.5 bg-primary text-white text-[12px] rounded hover:bg-red-700 transition-colors uppercase tracking-wider shadow-sm"
                 style="font-family:'JetBrains Mono',monospace;">
                <span class="material-symbols-outlined text-[16px] mr-1">download</span>
                Export All Lines to Excel
              </button>
              <div class="flex flex-col items-end border-l border-gray-200 pl-4">
                <span class="font-label-sm text-[10px] text-secondary uppercase">Last Scan</span>
                <span class="font-body-md text-[13px] font-bold">just now</span>
              </div>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-4 gap-sm mb-md shrink-0">
            <div class="bg-surface-container-lowest border border-gray-200 px-md py-2 rounded-DEFAULT">
              <p class="font-label-sm text-[10px] text-secondary uppercase">Total Lines</p>
              <p class="text-[24px] leading-tight font-bold text-gray-800" id="stat-total">0</p>
            </div>
            <div class="bg-surface-container-lowest border border-gray-200 px-md py-2 rounded-DEFAULT border-l-4 border-tertiary">
              <p class="font-label-sm text-[10px] uppercase text-tertiary">Verified</p>
              <p class="text-[24px] text-tertiary leading-tight font-bold" id="stat-verified">0</p>
            </div>
            <div class="bg-surface-container-lowest border border-gray-200 px-md py-2 rounded-DEFAULT border-l-4 border-primary">
              <p class="font-label-sm text-[10px] uppercase text-primary">Review Required</p>
              <p class="text-[24px] text-primary leading-tight font-bold" id="stat-review">0</p>
            </div>
            <div class="bg-surface-container-lowest border border-gray-200 px-md py-2 rounded-DEFAULT">
              <p class="font-label-sm text-[10px] text-secondary uppercase">Line Item Confidence</p>
              <p class="text-[24px] leading-tight font-bold text-gray-800" id="stat-confidence">-</p>
              <!-- hidden stub: app.py's renderResults writes to #stat-category; keep it so it never throws -->
              <span id="stat-category" style="display:none;"></span>
            </div>
          </div>

          <!-- ── Tabs: Sales Order | Sales Order Rows ─────────────────── -->
          <div class="flex items-end gap-1 border-b border-gray-200 mb-md shrink-0">
            <button id="tabbtn-order" onclick="switchOrderTab('order')"
              class="px-5 py-2 text-[12px] uppercase tracking-wider rounded-t border border-b-0 border-gray-200 bg-sidebar-dark text-white font-bold"
              style="font-family:'JetBrains Mono',monospace;">
              Sales Order
            </button>
            <button id="tabbtn-rows" onclick="switchOrderTab('rows')"
              class="px-5 py-2 text-[12px] uppercase tracking-wider rounded-t border border-b-0 border-gray-200 bg-white text-gray-500 hover:text-gray-800"
              style="font-family:'JetBrains Mono',monospace;">
              Sales Order Rows
            </button>
          </div>

          <!-- ── Tab 1: Sales Order (BSP header) ──────────────────────── -->
          <div id="tab-order" class="mb-md">""" + _sales_order_panel() + """
          </div>

          <!-- ── Tab 2: Sales Order Rows (line items table) ───────────── -->
          <section id="tab-rows" style="display:none; height:420px;"
                   class="bg-surface-container-lowest border border-gray-200 rounded-DEFAULT overflow-hidden flex-col shrink-0 shadow-sm mx-auto w-full">
            <div class="overflow-auto custom-scrollbar flex-grow min-h-0 bg-white">
              <table class="w-full text-left border-collapse">
                <thead class="sticky top-0 z-10">
                  <tr class="bg-sidebar-dark text-white border-b border-primary">
                    <th class="px-md py-3 text-[11px] uppercase tracking-wider border-r border-white/10 w-16">Line #</th>
                    <th class="px-md py-3 text-[11px] uppercase tracking-wider border-r border-white/10 w-14">Qty</th>
                    <th class="px-md py-3 text-[11px] uppercase tracking-wider border-r border-white/10">Item</th>
                    <th class="px-md py-3 text-[11px] uppercase tracking-wider border-r border-white/10">SKU</th>
                    <th class="px-md py-3 text-[11px] uppercase tracking-wider border-r border-white/10">Location</th>
                    <th class="px-md py-3 text-[11px] uppercase tracking-wider border-r border-white/10">Price</th>
                    <th class="px-md py-3 text-[11px] uppercase tracking-wider border-r border-white/10">Charge Type</th>
                    <th class="px-md py-3 text-[11px] uppercase tracking-wider border-r border-white/10">Period</th>
                    <th class="px-md py-3 text-[11px] uppercase tracking-wider border-r border-white/10">Fulfilment</th>
                    <th class="px-md py-3 text-[11px] uppercase tracking-wider border-r border-white/10">Confidence</th>
                    <th class="px-md py-3 text-[11px] uppercase tracking-wider">Status</th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-outline/10 text-sm font-medium" id="results-tbody"></tbody>
              </table>
            </div>
            <div class="px-md py-3 bg-gray-50 flex justify-between items-center border-t border-gray-200 shrink-0">
              <p class="font-label-sm text-[10px] text-secondary uppercase" id="results-count-label">Showing 0 lines</p>
              <div class="flex gap-2">
                <button class="px-3 py-1 bg-white border border-gray-300 text-[11px] rounded uppercase disabled:opacity-50" disabled>Prev</button>
                <button class="px-3 py-1 bg-white border border-gray-300 text-[11px] rounded uppercase disabled:opacity-50" disabled>Next</button>
              </div>
            </div>
          </section>

          <div class="mt-md grid grid-cols-1 md:grid-cols-2 gap-md shrink-0">
            <div class="border border-primary bg-white p-sm rounded flex gap-sm hover:bg-gray-50 transition-colors">
              <div class="bg-primary/10 p-2 rounded h-fit">
                <span class="material-symbols-outlined text-primary text-[20px]">lightbulb</span>
              </div>
              <div>
                <h3 class="text-[15px] font-semibold text-on-surface">Resolution Tip</h3>
                <p class="text-[12px] text-secondary leading-tight mt-0.5">Material code mismatches are marked ERR_404. Contact MDM to sync product catalogue.</p>
              </div>
            </div>
            <div class="border border-primary bg-white p-sm rounded flex gap-sm hover:bg-gray-50 transition-colors">
              <div class="bg-primary/10 p-2 rounded h-fit">
                <span class="material-symbols-outlined text-primary text-[20px]">auto_awesome</span>
              </div>
              <div>
                <h3 class="text-[15px] font-semibold text-on-surface">Intelligence</h3>
                <p class="text-[12px] text-secondary leading-tight mt-0.5">Once verified, agent generates the final validated Excel table automatically.</p>
              </div>
            </div>
          </div>

          <div class="mt-lg pt-4 border-t border-outline/10 text-center shrink-0 mb-4">
            <p class="font-label-sm text-[10px] text-secondary italic">Privacy Note: Data is not retained in-app. Download your Excel extract now; it will be cleared when you leave this page.</p>
          </div>
        </div>
      </main>
    </div>

    <script>
      // ── Sales Order tabs + BSP header rendering ─────────────────────
      function switchOrderTab(which) {
        const orderTab = document.getElementById('tab-order');
        const rowsTab = document.getElementById('tab-rows');
        const orderBtn = document.getElementById('tabbtn-order');
        const rowsBtn = document.getElementById('tabbtn-rows');
        const on = 'bg-sidebar-dark text-white font-bold';
        const off = 'bg-white text-gray-500 hover:text-gray-800';
        if (which === 'order') {
          orderTab.style.display = 'block'; rowsTab.style.display = 'none';
          orderBtn.className = orderBtn.className.replace(off, on);
          rowsBtn.className = rowsBtn.className.replace(on, off);
        } else {
          orderTab.style.display = 'none'; rowsTab.style.display = 'flex';
          rowsBtn.className = rowsBtn.className.replace(off, on);
          orderBtn.className = orderBtn.className.replace(on, off);
        }
      }

      function renderSalesOrderHeader() {
        const order = ((window.RESULT || RESULT || {}).order) || {};
        document.querySelectorAll('[data-bsp]').forEach(el => {
          const v = order[el.getAttribute('data-bsp')];
          const empty = (v === null || v === undefined || v === '' || v === 'Not Specified');
          el.innerText = empty ? 'Not Specified' : String(v);
          el.classList.toggle('text-secondary', empty);
          el.classList.toggle('italic', empty);
        });
      }

      // ── Excel export: Sheet 1 = Sales Order, Sheet 2 = Sales Order Rows ──
      const BSP_EXPORT_FIELDS = [
        ["order_title", "Order Title"], ["order_type", "Order Type"],
        ["order_category", "Order Category"], ["status", "Status"],
        ["contract_signed_date", "Contract Signed Date"], ["customer_contact", "Customer Contact"],
        ["location_count", "Location Count"], ["external_reference_number", "External Reference Number"],
        ["company_code", "Company Code"], ["bill_to_party", "Bill To Party"],
        ["ship_to_party", "Ship To Party"], ["order_date", "Order Date"],
        ["sales_contact", "Sales Contact"], ["account_manager", "Account Manager"],
        ["short_description", "Short Description"], ["escalation_level_priority", "Escalation Level (Priority)"],
        ["customer_required_date", "Customer Required Date"], ["customer_reference", "Customer Reference"],
        ["device_services", "Device Services"], ["description", "Description"]
      ];

      function exportExcelTwoSheets() {
        const result = (window.RESULT || RESULT || {});
        const order = result.order || {};
        const lines = order.line_items || [];

        // Sheet 1: Sales Order (Field | Value)
        const headerAoA = [["Field", "Value"]].concat(
          BSP_EXPORT_FIELDS.map(([k, label]) => [label, (order[k] == null ? "" : String(order[k]))])
        );
        const ws1 = XLSX.utils.aoa_to_sheet(headerAoA);
        ws1['!cols'] = [{ wch: 28 }, { wch: 70 }];

        // Sheet 2: Sales Order Rows
        const rows = lines.map((li, i) => ({
          "Line": i + 1, "SKU": li.sku || "", "Item": li.item || "", "Location": li.location || "",
          "Quantity": li.quantity || "", "Price": li.price || "", "Charge Type": li.charge_type || "",
          "Period": li.recurring_period || "", "Fulfilment": li.fulfilment || "",
          "Confidence": li.confidence || ""
        }));
        const ws2 = XLSX.utils.json_to_sheet(rows.length ? rows : [{"Line":"","SKU":"","Item":"","Location":"","Quantity":"","Price":"","Charge Type":"","Period":"","Fulfilment":"","Confidence":""}]);
        ws2['!cols'] = [{wch:6},{wch:20},{wch:40},{wch:30},{wch:9},{wch:12},{wch:12},{wch:14},{wch:14}];

        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws1, "Sales Order");
        XLSX.utils.book_append_sheet(wb, ws2, "Sales Order Rows");
        XLSX.writeFile(wb, "Q2O_" + ((typeof OPP !== 'undefined' && OPP) || 'export') + "_sales_order.xlsx");
      }

      // ── Rows table renderer: exact OrderLineItem fields ─────────────
      function renderRowsTable() {
        const order = ((window.RESULT || RESULT || {}).order) || {};
        const lines = order.line_items || [];
        const g = (li, k) => { const v = li[k]; return (v === null || v === undefined || v === '') ? 'Not Specified' : String(v); };
        document.getElementById('results-tbody').innerHTML = lines.map((li, i) => {
          const ful = g(li, 'fulfilment');
          const missing = ful === 'Not Specified';
          const fulCell = missing ? `
            <td class="px-md py-2 bg-error-container/40 border-r border-outline/10 relative">
              <div class="flex items-center justify-between text-primary">
                <span class="font-label-sm text-[11px] font-bold">ERR_404</span>
                <span class="material-symbols-outlined text-primary text-[16px]">warning</span>
              </div></td>` : `
            <td class="px-md py-2 font-label-sm text-[11px] border-r border-outline/10 font-mono">${esc(ful)}</td>`;
          const badge = missing ? `
            <span class="inline-flex items-center gap-1 px-2 py-0.5 bg-error-container text-primary rounded-full text-[10px] uppercase font-bold">
              <span class="material-symbols-outlined text-[14px]">priority_high</span> Review</span>` : `
            <span class="inline-flex items-center gap-1 px-2 py-0.5 bg-tertiary/10 text-tertiary rounded-full text-[10px] uppercase font-bold">
              <span class="material-symbols-outlined text-[14px]" style="font-variation-settings:'FILL' 1;">check_circle</span> Verified</span>`;
          // confidence pill (High=green, Medium=amber, Low/None=red)
          let conf = g(li, 'confidence');
          if (conf === 'Not Specified' || !conf) conf = 'None';
          const cl = conf.toLowerCase();
          const confColor = cl === 'high' ? 'bg-tertiary/10 text-tertiary'
                          : cl === 'medium' ? 'bg-amber-100 text-amber-700'
                          : (cl === 'low' || cl === 'none') ? 'bg-error-container text-primary'
                          : 'bg-gray-100 text-gray-500';
          const confCell = `
            <td class="px-md py-2 border-r border-outline/10">
              <span class="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] uppercase font-bold ${confColor}">${esc(conf)}</span></td>`;
          return `
          <tr class="hover:bg-gray-50 transition-colors group">
            <td class="px-md py-2 font-label-sm text-[11px] text-secondary border-r border-outline/10">${String(i+1).padStart(3,'0')}</td>
            <td class="px-md py-2 border-r border-outline/10 font-mono">${esc(g(li,'quantity'))}</td>
            <td class="px-md py-2 font-semibold border-r border-outline/10">${esc(g(li,'item'))}</td>
            <td class="px-md py-2 font-label-sm text-[11px] border-r border-outline/10 font-mono">${esc(g(li,'sku'))}</td>
            <td class="px-md py-2 border-r border-outline/10">${esc(g(li,'location'))}</td>
            <td class="px-md py-2 border-r border-outline/10 font-mono">${esc(g(li,'price'))}</td>
            <td class="px-md py-2 border-r border-outline/10">${esc(g(li,'charge_type'))}</td>
            <td class="px-md py-2 border-r border-outline/10">${esc(g(li,'recurring_period'))}</td>
            ${fulCell}
            ${confCell}
            <td class="px-md py-2">${badge}</td>
          </tr>`;
        }).join('') || '<tr><td colspan="11" class="px-md py-6 text-center text-secondary text-sm">No order lines extracted. Run the order process first.</td></tr>';
      }

      // ── 4th stat: Line Item Confidence ───────────────────────────────
      // % of line-item fields (across all lines) that are populated.
      function renderLineConfidence() {
        const el = document.getElementById('stat-confidence');
        if (!el) return;
        const lines = (((window.RESULT || RESULT || {}).order) || {}).line_items || [];
        if (!lines.length) { el.innerText = '-'; return; }
        const KEYS = ['quantity','item','sku','location','price','charge_type','recurring_period','fulfilment'];
        let filled = 0, total = 0;
        lines.forEach(li => KEYS.forEach(k => {
          total++;
          const v = li[k];
          if (!(v === null || v === undefined || v === '' || v === 'Not Specified')) filled++;
        }));
        el.innerText = Math.round(100 * filled / total) + '%';
      }

      // Hook into the main controller AFTER it is defined
      // (the controller script runs after this one; DOMContentLoaded runs last).
      window.addEventListener('DOMContentLoaded', function () {
        if (typeof renderResults === 'function') {
          const _origRenderResults = renderResults;
          renderResults = function () {
            _origRenderResults();      // stats, subtitles
            renderRowsTable();         // rebuild tbody with model-exact columns
            renderSalesOrderHeader();
            renderLineConfidence();
            switchOrderTab('order');   // Sales Order first, then rows
          };
        }
        // Replace the controller's single-sheet export with the 2-sheet one
        exportExcel = exportExcelTwoSheets;
      });
    </script>
    """
