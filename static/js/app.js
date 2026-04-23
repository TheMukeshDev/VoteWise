// Global UI State
const views = ['chat', 'dashboard', 'timeline', 'polling', 'help'];

// --- Sidebar Mobile Toggle ---
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar.classList.contains('-translate-x-full')) {
        sidebar.classList.remove('-translate-x-full');
    } else {
        sidebar.classList.add('-translate-x-full');
    }
}

// --- Navigation Logic ---
function switchTab(tabName) {
    // Update active nav button styles
    views.forEach(v => {
        const btn = document.getElementById(`nav-${v}`);
        if(btn) {
            if(v === tabName) {
                btn.className = "w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all text-white bg-brand-500/10 border-l-4 border-brand-500";
                btn.querySelector('i').classList.add('text-brand-500');
            } else {
                btn.className = "w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium text-slate-400 hover:text-white hover:bg-slate-800/50 transition-all border-l-4 border-transparent";
                btn.querySelector('i').classList.remove('text-brand-500');
            }
        }
    });

    // Show/Hide views
    views.forEach(v => {
        const el = document.getElementById(`view-${v}`);
        if(el) {
            if(v === tabName) {
                el.classList.remove('hidden');
                el.classList.add('flex');
                if(v !== 'chat') el.classList.replace('flex', 'block'); // Adjust flex vs block based on view
            } else {
                el.classList.add('hidden');
                el.classList.remove('flex');
            }
        }
    });

    // Close sidebar on mobile after click
    if(window.innerWidth < 768) {
        document.getElementById('sidebar').classList.add('-translate-x-full');
    }

    // Load dynamic data
    if(tabName === 'timeline') loadTimelineData();
}

// --- Chat Logic ---
function handleEnter(e) {
    if (e.key === 'Enter') sendChatMessage();
}

function sendQuickAction(text) {
    const input = document.getElementById('chat-input');
    input.value = text;
    sendChatMessage();
    switchTab('chat');
}

function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    if (!message) return;

    // 1. Add User Message
    addUserMessageToDOM(message);
    input.value = '';

    // 2. Add Loading Indicator
    const loadingId = 'loading-' + Date.now();
    addLoadingMessageToDOM(loadingId);

    // Scroll to bottom
    scrollToBottom();

    // 3. API Call
    fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: message })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById(loadingId).remove();
        addAIMessageToDOM(data);
    })
    .catch(err => {
        document.getElementById(loadingId).remove();
        addAIMessageToDOM({
            intro: "Sorry, I'm having trouble connecting to the server.",
            steps: [], tips: [], actions: []
        });
    });
}

function addUserMessageToDOM(text) {
    const chatContainer = document.getElementById('chat-messages');
    const msgHTML = `
        <div class="flex gap-4 w-full justify-end animate-fade-in-up">
            <div class="flex flex-col gap-2 max-w-[85%] md:max-w-[75%] items-end">
                <div class="bg-brand-600/20 border border-brand-500/30 p-4 rounded-2xl rounded-tr-sm text-brand-50 text-sm md:text-base leading-relaxed backdrop-blur-md shadow-lg">
                    ${text}
                </div>
            </div>
            <div class="w-10 h-10 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center flex-shrink-0 text-slate-400">
                <i class="fa-solid fa-user text-sm"></i>
            </div>
        </div>
    `;
    chatContainer.insertAdjacentHTML('beforeend', msgHTML);
}

function addLoadingMessageToDOM(id) {
    const chatContainer = document.getElementById('chat-messages');
    const msgHTML = `
        <div class="flex gap-4 w-full animate-fade-in-up" id="${id}">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500 to-purple-600 flex items-center justify-center flex-shrink-0 shadow-lg shadow-brand-500/20">
                <i class="fa-solid fa-robot text-white text-sm"></i>
            </div>
            <div class="flex flex-col gap-2 max-w-[85%] md:max-w-[75%]">
                <div class="glass-panel px-5 py-4 rounded-2xl rounded-tl-sm flex items-center gap-3 text-slate-300 text-sm">
                    <i class="fa-solid fa-circle-notch fa-spin text-brand-400"></i> Thinking...
                </div>
            </div>
        </div>
    `;
    chatContainer.insertAdjacentHTML('beforeend', msgHTML);
}

function addAIMessageToDOM(data) {
    const chatContainer = document.getElementById('chat-messages');
    
    let contentHtml = `<div class="glass-panel p-5 rounded-2xl rounded-tl-sm text-slate-200 text-sm md:text-base leading-relaxed">`;
    
    // Intro
    if(data.intro) {
        contentHtml += `<p class="font-medium text-white mb-3">${data.intro}</p>`;
    }
    
    // Steps
    if(data.steps && data.steps.length > 0) {
        contentHtml += `<ul class="list-disc pl-5 space-y-2 mb-4 text-slate-300">`;
        data.steps.forEach(step => {
            contentHtml += `<li>${step}</li>`;
        });
        contentHtml += `</ul>`;
    }
    
    // Tips
    if(data.tips && data.tips.length > 0) {
        data.tips.forEach(tip => {
            contentHtml += `
                <div class="bg-brand-500/10 border-l-4 border-brand-500 p-3 rounded-r-lg mb-3 text-brand-100 text-sm flex items-start gap-2">
                    <i class="fa-solid fa-lightbulb text-brand-400 mt-1"></i>
                    <span>${tip}</span>
                </div>
            `;
        });
    }
    
    // Actions
    if(data.actions && data.actions.length > 0) {
        contentHtml += `<div class="flex flex-wrap gap-2 mt-4 pt-4 border-t border-slate-700/50">`;
        data.actions.forEach(action => {
            contentHtml += `
                <button onclick="sendQuickAction('${action}')" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-brand-600 border border-slate-700 hover:border-brand-500 text-slate-300 hover:text-white text-xs font-medium transition-colors">
                    ${action}
                </button>
            `;
        });
        contentHtml += `</div>`;
    }
    
    contentHtml += `</div>`;

    const msgHTML = `
        <div class="flex gap-4 w-full animate-fade-in-up">
            <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-500 to-purple-600 flex items-center justify-center flex-shrink-0 shadow-lg shadow-brand-500/20">
                <i class="fa-solid fa-robot text-white text-sm"></i>
            </div>
            <div class="flex flex-col gap-2 max-w-[85%] md:max-w-[75%]">
                ${contentHtml}
            </div>
        </div>
    `;
    
    chatContainer.insertAdjacentHTML('beforeend', msgHTML);
    scrollToBottom();
}

function scrollToBottom() {
    const scrollContainer = document.getElementById('main-scroll');
    scrollContainer.scrollTo({
        top: scrollContainer.scrollHeight,
        behavior: 'smooth'
    });
}

// --- Data Fetching Logic ---
let timelineLoaded = false;
function loadTimelineData() {
    if(timelineLoaded) return;
    
    const container = document.getElementById('timeline-grid');
    
    fetch('/api/election/timeline')
    .then(res => res.json())
    .then(response => {
        const data = response.data || [];
        container.innerHTML = '';
        if(data.length === 0) {
            container.innerHTML = '<p class="text-slate-400">No upcoming events found.</p>';
            return;
        }
        
        data.forEach(item => {
            container.innerHTML += `
                <div class="glass-panel p-6 rounded-2xl flex flex-col hover:border-brand-500/50 transition-colors">
                    <div class="flex justify-between items-start mb-4">
                        <div class="w-12 h-12 rounded-xl bg-brand-500/10 text-brand-400 flex items-center justify-center text-xl">
                            <i class="fa-solid fa-calendar"></i>
                        </div>
                        <span class="px-3 py-1 bg-slate-800 text-slate-300 text-xs rounded-full border border-slate-700">${item.date}</span>
                    </div>
                    <h3 class="text-lg font-semibold text-white mb-4 flex-1">${item.event}</h3>
                    <button onclick="setReminder('${item.event}', '${item.date}')" class="w-full py-2.5 bg-slate-800 hover:bg-brand-600 text-white rounded-xl text-sm font-medium transition-colors border border-slate-700 hover:border-brand-500">
                        <i class="fa-solid fa-bell mr-2"></i> Set Reminder
                    </button>
                </div>
            `;
        });
        timelineLoaded = true;
    })
    .catch(() => {
        container.innerHTML = '<p class="text-red-400">Failed to load timeline.</p>';
    });
}

function searchPollingBooth() {
    const input = document.getElementById('polling-input');
    const location = input.value.trim();
    if(!location) return;

    const resultsDiv = document.getElementById('polling-results');
    resultsDiv.classList.remove('hidden');
    resultsDiv.innerHTML = '<div class="text-slate-400 p-6"><i class="fa-solid fa-circle-notch fa-spin mr-2 text-brand-500"></i> Searching database...</div>';

    fetch(`/api/polling?lat=28.6139&lng=77.2090`)
    .then(res => res.json())
    .then(response => {
        const data = response.data;
        if(response.status === 'success') {
            document.getElementById('pb-name').innerText = data.booth_name;
            document.getElementById('pb-address').innerText = data.address;
            document.getElementById('pb-distance').innerText = data.distance_km;
            document.getElementById('pb-link').href = data.map_link;
            
            // Re-render HTML to restore original structure but with data
            resultsDiv.innerHTML = `
                <div class="p-6 rounded-xl border border-brand-500/30 bg-brand-500/5 relative overflow-hidden">
                    <div class="absolute top-0 right-0 w-32 h-32 bg-brand-500/10 rounded-full blur-2xl"></div>
                    
                    <div class="flex flex-col md:flex-row items-start gap-6 relative z-10">
                        <div class="w-14 h-14 rounded-full bg-brand-500 text-white flex items-center justify-center text-2xl flex-shrink-0 shadow-[0_0_15px_rgba(99,102,241,0.4)]">
                            <i class="fa-solid fa-building-flag"></i>
                        </div>
                        <div class="flex-1">
                            <h3 class="text-xl font-bold text-white mb-2">${data.booth_name}</h3>
                            <div class="space-y-2 mb-6">
                                <p class="text-slate-300 flex items-center gap-3"><i class="fa-solid fa-location-dot text-brand-400 w-4 text-center"></i> <span>${data.address}</span></p>
                                <p class="text-slate-400 text-sm flex items-center gap-3"><i class="fa-solid fa-person-walking text-slate-500 w-4 text-center"></i> <span>Approx. ${data.distance_km} km away from your location</span></p>
                            </div>
                            <a href="${data.map_link}" target="_blank" class="inline-flex items-center justify-center w-full md:w-auto gap-2 px-6 py-3 rounded-xl bg-slate-800 hover:bg-brand-600 text-white font-medium border border-slate-600 hover:border-brand-500 transition-colors shadow-lg">
                                <i class="fa-solid fa-map"></i> Open in Google Maps
                            </a>
                        </div>
                    </div>
                </div>
            `;
        }
    });
}

// Global reminder function
window.setReminder = function(eventName, eventDate) {
    alert(`Generating calendar invite for ${eventName}...`);
    
    fetch('/api/reminder/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            event_name: eventName, 
            event_date: eventDate 
        })
    })
    .then(response => {
        if (!response.ok) throw new Error('Failed to generate invite');
        return response.blob();
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `votewise_${eventDate.replace(/ /g, '_')}.ics`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
    })
    .catch(error => {
        console.error('Error setting reminder:', error);
        alert('Could not set reminder at this time.');
    });
};
