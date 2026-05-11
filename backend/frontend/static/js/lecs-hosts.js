(function() {
    'use strict';

    const API = '/api/v1/lecs-hosts';

    const STATUS_LABELS = {
        creating: '创建中', normal: '正常', failed: '创建失败',
        shutting_down: '关机中', stopped: '已关机', starting: '启动中', deleting: '删除中'
    };

    const STATE_CONFIG = {
        creating: { canShutdown: false, canStart: false, canDelete: false },
        normal: { canShutdown: true, canStart: false, canDelete: false },
        failed: { canShutdown: false, canStart: true, canDelete: true },
        shutting_down: { canShutdown: false, canStart: false, canDelete: false },
        stopped: { canShutdown: false, canStart: true, canDelete: true },
        starting: { canShutdown: false, canStart: false, canDelete: false },
        deleting: { canShutdown: false, canStart: false, canDelete: false }
    };

    const TRANSITIONAL_STATES = ['creating', 'shutting_down', 'starting', 'deleting'];
    const VALID_DURATIONS = [1,2,3,4,5,6,7,8,9,12,24];
    const VALID_OS = { huawei_euler: 'Huawei Euler OS', ubuntu: 'Ubuntu', windows: 'Windows' };

    let pricingData = null;
    let selectedSpecId = null;
    let pollInterval = null;
    let currentPage = 1;
    let currentPageSize = 20;

    function apiFetch(url, opts = {}) {
        const defaults = { credentials: 'include', headers: {} };
        if (opts.body && typeof opts.body !== 'string') {
            defaults.headers['Content-Type'] = 'application/json';
            opts.body = JSON.stringify(opts.body);
        }
        return fetch(url, { ...defaults, ...opts, headers: { ...defaults.headers, ...opts.headers } })
            .then(r => r.json().then(d => ({ status: r.status, ok: r.ok, data: d })));
    }

    function statusLabel(s) { return STATUS_LABELS[s] || s; }
    function badgeClass(s) { return 'status-badge badge-' + s; }
    function billingLabel(m) { return m === 'subscription' ? '包年/包月' : '按需计费'; }

    function hasTransitional(hosts) {
        return hosts.some(h => TRANSITIONAL_STATES.includes(h.status));
    }

    // ---- LIST PAGE ----
    function initListPage() {
        fetchHosts();
        document.getElementById('lecsPrevPage').addEventListener('click', function() {
            if (currentPage > 1) { currentPage--; fetchHosts(); }
        });
        document.getElementById('lecsNextPage').addEventListener('click', function() {
            currentPage++; fetchHosts();
        });
    }

    function fetchHosts() {
        apiFetch(API + '?page=' + currentPage + '&page_size=' + currentPageSize)
            .then(r => {
                if (r.ok && r.data.status === 'success') {
                    renderHosts(r.data.data);
                }
            });
    }

    function renderHosts(paged) {
        var tbody = document.getElementById('lecsHostTableBody');
        var emptyEl = document.getElementById('lecsEmptyState');
        var paginationEl = document.getElementById('lecsPagination');
        tbody.innerHTML = '';

        if (!paged.items || paged.items.length === 0) {
            emptyEl.style.display = 'block';
            paginationEl.style.display = 'none';
            return;
        }
        emptyEl.style.display = 'none';

        paged.items.forEach(function(h) {
            var tr = document.createElement('tr');
            var cfg = STATE_CONFIG[h.status] || { canShutdown:false, canStart:false, canDelete:false };
            var disabledAttr = function(enabled) { return enabled ? '' : 'disabled'; };

            tr.innerHTML =
                '<td><div class="lecs-hostname">' + escapeHtml(h.hostname) + '</div>' +
                '<div class="lecs-host-id">' + escapeHtml(h.id.substring(0,8)) + '</div></td>' +
                '<td>' + billingLabel(h.billing_mode) + '</td>' +
                '<td><span class="' + badgeClass(h.status) + '" data-testid="lecs-host-status-' + h.id + '">' +
                    statusLabel(h.status) + '</span></td>' +
                '<td>' + (h.ip_mode === 'dhcp' ? 'DHCP' : escapeHtml(h.ip_address || '')) + '</td>' +
                '<td><div class="action-group">' +
                    '<button class="action-btn" ' + disabledAttr(cfg.canShutdown) +
                        ' data-testid="lecs-host-action-shutdown" data-id="' + h.id + '">关机</button>' +
                    '<button class="action-btn" ' + disabledAttr(cfg.canStart) +
                        ' data-testid="lecs-host-action-start" data-id="' + h.id + '">启动</button>' +
                    '<button class="action-btn delete-btn" ' + disabledAttr(cfg.canDelete) +
                        ' data-testid="lecs-host-action-delete" data-id="' + h.id + '">删除</button>' +
                '</div></td>';

            tbody.appendChild(tr);
        });

        // Attach event listeners
        tbody.querySelectorAll('.action-btn[disabled]').forEach(function(btn) {
            // Already disabled by attribute, no click handler needed
        });
        tbody.querySelectorAll('.action-btn:not([disabled])').forEach(function(btn) {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                handleAction(btn.getAttribute('data-id'), btn.textContent.trim());
            });
        });

        // Pagination
        paginationEl.style.display = 'flex';
        document.getElementById('lecsPageNumber').textContent = paged.page;
        document.getElementById('lecsPaginationInfo').textContent =
            '共 ' + paged.total + ' 条，第 ' + paged.page + '/' + paged.total_pages + ' 页';
        document.getElementById('lecsPrevPage').disabled = (paged.page <= 1);
        document.getElementById('lecsNextPage').disabled = (paged.page >= paged.total_pages);

        // Polling
        if (pollInterval) { clearInterval(pollInterval); pollInterval = null; }
        if (hasTransitional(paged.items)) {
            pollInterval = setInterval(fetchHosts, 3000);
        }
    }

    function handleAction(hostId, action) {
        if (action === '关机') {
            apiFetch(API + '/' + hostId + '/shutdown', { method: 'POST' })
                .then(function() { fetchHosts(); });
        } else if (action === '启动') {
            apiFetch(API + '/' + hostId + '/start', { method: 'POST' })
                .then(function() { fetchHosts(); });
        } else if (action === '删除') {
            if (confirm('确定要删除该主机吗？此操作不可恢复。')) {
                apiFetch(API + '/' + hostId, { method: 'DELETE' })
                    .then(function() { fetchHosts(); });
            }
        }
    }

    // ---- CREATE PAGE ----
    function initCreatePage() {
        // Fetch pricing
        apiFetch(API + '/pricing').then(function(r) {
            if (r.ok && r.data.status === 'success') {
                pricingData = r.data.data;
                renderSpecCards('economy');
            }
        });

        // Populate mask dropdown
        var maskSel = document.getElementById('maskSelect');
        if (maskSel) {
            for (var i = 8; i <= 24; i++) {
                var opt = document.createElement('option');
                opt.value = i; opt.textContent = i;
                maskSel.appendChild(opt);
            }
        }

        // Instance type tabs
        document.querySelectorAll('input[name="instance_type"]').forEach(function(radio) {
            radio.addEventListener('change', function() {
                selectInstanceType(this.value);
            });
        });

        // IP mode tabs
        document.querySelectorAll('input[name="ip_mode"]').forEach(function(radio) {
            radio.addEventListener('change', function() {
                document.getElementById('manualIpFields').style.display =
                    this.value === 'manual' ? 'block' : 'none';
            });
        });

        // Duration & billing mode & spec change → cost update
        document.querySelectorAll('input[name="billing_mode"]').forEach(function(r) {
            r.addEventListener('change', updateCost);
        });
        document.querySelectorAll('input[name="duration"]').forEach(function(r) {
            r.addEventListener('change', updateCost);
        });

        // Default select 1 month
        var oneMonth = document.querySelector('input[name="duration"][value="1"]');
        if (oneMonth) oneMonth.checked = true;

        // Validation on input
        var hostnameInput = document.getElementById('hostnameInput');
        if (hostnameInput) hostnameInput.addEventListener('input', function() {
            validateHostname(this.value);
        });
        var usernameInput = document.getElementById('usernameInput');
        if (usernameInput) usernameInput.addEventListener('input', function() {
            validateUsername(this.value);
        });
        var passwordInput = document.getElementById('passwordInput');
        if (passwordInput) passwordInput.addEventListener('input', function() {
            validatePassword(this.value);
        });

        // Buy button
        document.getElementById('buyButton').addEventListener('click', function() {
            if (validateCreateForm()) showConfirmDialog();
        });

        // Confirm dialog buttons
        document.getElementById('confirmCancelBtn').addEventListener('click', hideConfirmDialog);
        document.getElementById('confirmOkBtn').addEventListener('click', submitCreate);
    }

    function selectInstanceType(type) {
        document.querySelectorAll('.radio-group input[name="instance_type"]').forEach(function(r) {
            r.parentElement.classList.toggle('selected', r.checked);
        });
        selectedSpecId = null;
        renderSpecCards(type);
        updateCost();
    }

    function renderSpecCards(type) {
        var grid = document.getElementById('specGrid');
        grid.innerHTML = '';
        var specs = pricingData ? pricingData[type] || [] : [];
        specs.forEach(function(s) {
            var card = document.createElement('div');
            card.className = 'spec-card';
            card.setAttribute('data-testid', 'lecs-instance-card-' + s.spec_id);
            card.setAttribute('data-id', s.spec_id);
            card.innerHTML =
                '<div class="spec-card-name">' + s.name + '</div>' +
                '<div class="spec-card-details">' + s.vcpu + 'vCPU · ' + s.ram_gb + 'GiB · ' +
                    s.system_disk_gb + 'G系统盘</div>' +
                '<div class="spec-card-price">¥' + s.monthly_price + '/月</div>';
            card.addEventListener('click', function() {
                grid.querySelectorAll('.spec-card').forEach(function(c) { c.classList.remove('selected'); });
                card.classList.add('selected');
                selectedSpecId = s.spec_id;
                updateCost();
            });
            grid.appendChild(card);
        });
    }

    function getSelectedSpec() {
        if (!pricingData || !selectedSpecId) return null;
        var all = [].concat(pricingData.economy || [], pricingData.high_performance || []);
        return all.find(function(s) { return s.spec_id === selectedSpecId; });
    }

    function updateCost() {
        var spec = getSelectedSpec();
        var billingMode = document.querySelector('input[name="billing_mode"]:checked');
        var durationRadio = document.querySelector('input[name="duration"]:checked');
        var displayEl = document.getElementById('costDisplay');
        if (!spec || !durationRadio) { displayEl.textContent = '请选择实例规格'; return; }
        var months = parseInt(durationRadio.value);
        var price = spec.monthly_price;
        if (billingMode && billingMode.value === 'subscription') {
            var total = price * months;
            displayEl.textContent = '¥' + total + ' (' + months + '个月，' + price + '元/月)';
        } else {
            var daily = price / 30;
            displayEl.textContent = '¥' + daily.toFixed(2) + '/天';
        }
    }

    function validateHostname(v) {
        var err = document.getElementById('hostnameError');
        var inp = document.getElementById('hostnameInput');
        if (!v || v.startsWith('_') || !/^[\w]{4,10}$/.test(v)) {
            err.textContent = '主机名仅支持英文、数字、下划线，长度4-10字符，不可以下划线开头';
            inp.classList.add('input-error'); return false;
        }
        err.textContent = ''; inp.classList.remove('input-error'); return true;
    }

    function validateUsername(v) {
        var err = document.getElementById('usernameError');
        var inp = document.getElementById('usernameInput');
        if (!v || !/^[a-zA-Z0-9_@.+\-]{4,16}$/.test(v)) {
            err.textContent = '用户名长度4-16字符';
            inp.classList.add('input-error'); return false;
        }
        err.textContent = ''; inp.classList.remove('input-error'); return true;
    }

    function validatePassword(v) {
        var err = document.getElementById('passwordError');
        var inp = document.getElementById('passwordInput');
        if (!v || !/^[a-zA-Z0-9_@#$%^&+=!\-]{8,32}$/.test(v)) {
            err.textContent = '密码长度8-32字符';
            inp.classList.add('input-error'); return false;
        }
        err.textContent = ''; inp.classList.remove('input-error'); return true;
    }

    function validateCreateForm() {
        var ok = true;
        if (!validateHostname(document.getElementById('hostnameInput').value)) ok = false;
        if (!validateUsername(document.getElementById('usernameInput').value)) ok = false;
        if (!validatePassword(document.getElementById('passwordInput').value)) ok = false;
        if (!selectedSpecId) {
            document.getElementById('specError').textContent = '请选择有效的实例规格'; ok = false;
        } else { document.getElementById('specError').textContent = ''; }
        var ipMode = document.querySelector('input[name="ip_mode"]:checked').value;
        if (ipMode === 'manual') {
            var ip = document.getElementById('ipInput').value;
            var mask = document.getElementById('maskSelect').value;
            if (!ip || !/^(?:(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)$/.test(ip)) {
                document.getElementById('ipError').textContent = '请输入有效的IP地址'; ok = false;
            } else { document.getElementById('ipError').textContent = ''; }
            var maskNum = parseInt(mask);
            if (maskNum < 8 || maskNum > 24) {
                document.getElementById('maskError').textContent = '请选择有效的掩码值'; ok = false;
            } else { document.getElementById('maskError').textContent = ''; }
        }
        var dur = document.querySelector('input[name="duration"]:checked');
        if (!dur) { ok = false; }
        return ok;
    }

    function showConfirmDialog() {
        var spec = getSelectedSpec();
        var billingMode = document.querySelector('input[name="billing_mode"]:checked');
        var durationRadio = document.querySelector('input[name="duration"]:checked');
        var ipMode = document.querySelector('input[name="ip_mode"]:checked');

        var costText = document.getElementById('costDisplay').textContent;
        var rows = [
            { label: '计费模式', value: billingMode.value === 'subscription' ? '包年/包月' : '按需计费' },
            { label: '主机名', value: document.getElementById('hostnameInput').value },
            { label: '实例类型', value: billingMode.value },
            { label: '实例规格', value: spec ? spec.name + ' (' + spec.vcpu + 'vCPU/' + spec.ram_gb + 'GiB)' : '' },
            { label: '操作系统', value: VALID_OS[document.getElementById('osSelect').value] || '' },
            { label: 'IP配置', value: ipMode.value + (ipMode.value === 'manual' ? ' ' + document.getElementById('ipInput').value : '') },
            { label: '购买时长', value: durationRadio ? durationRadio.value + '个月' : '' },
            { label: '配置费用', value: costText, isTotal: true }
        ];

        var html = '';
        rows.forEach(function(r) {
            html += '<div class="summary-row' + (r.isTotal ? ' summary-total' : '') + '">' +
                '<span class="summary-label">' + r.label + '</span>' +
                '<span class="summary-value">' + escapeHtml(r.value) + '</span></div>';
        });
        document.getElementById('confirmSummary').innerHTML = html;
        document.getElementById('confirmDialog').style.display = 'flex';
    }

    function hideConfirmDialog() {
        document.getElementById('confirmDialog').style.display = 'none';
    }

    function submitCreate() {
        var billingMode = document.querySelector('input[name="billing_mode"]:checked').value;
        var ipMode = document.querySelector('input[name="ip_mode"]:checked').value;
        var durationRadio = document.querySelector('input[name="duration"]:checked');
        var spec = getSelectedSpec();

        var body = {
            hostname: document.getElementById('hostnameInput').value,
            billing_mode: billingMode,
            instance_type: document.querySelector('input[name="instance_type"]:checked').value,
            spec_id: selectedSpecId,
            os_image: document.getElementById('osSelect').value,
            ip_mode: ipMode,
            ip_address: ipMode === 'manual' ? document.getElementById('ipInput').value : null,
            ip_mask: ipMode === 'manual' ? parseInt(document.getElementById('maskSelect').value) : null,
            username: document.getElementById('usernameInput').value,
            password: document.getElementById('passwordInput').value,
            duration: durationRadio ? parseInt(durationRadio.value) : 1
        };

        apiFetch(API, { method: 'POST', body: body }).then(function(r) {
            hideConfirmDialog();
            if (r.ok && r.data.status === 'success') {
                window.location.href = '/console/lecs-hosts/list';
            } else {
                var msg = r.data && r.data.message ? r.data.message : '创建失败，请重试';
                if (r.data && r.data.detail) msg = r.data.detail.message || r.data.detail;
                alert(msg);
            }
        });
    }

    function escapeHtml(text) {
        var div = document.createElement('div');
        div.appendChild(document.createTextNode(text));
        return div.innerHTML;
    }

    // ---- INIT ----
    document.addEventListener('DOMContentLoaded', function() {
        if (window.location.pathname.indexOf('/console/lecs-hosts/list') !== -1) {
            initListPage();
        } else if (window.location.pathname.indexOf('/console/lecs-hosts/create') !== -1) {
            initCreatePage();
        }
    });
})();
