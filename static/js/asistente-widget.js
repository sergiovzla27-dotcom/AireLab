/* ============================================
   AireLab - Widget Asistente Flotante
   Chat funcional en todas las páginas
   ============================================ */

(function() {
    'use strict';
    
    // Si estamos en /asistente, no cargar
    if (window.location.pathname === '/asistente') return;
    
    // ============================================
    // HTML del widget
    // ============================================
    const widgetHTML = `
        <button id="asisBtnAbrir" class="asis-w-btn" title="Pregúntame">
            <i data-lucide="bot"></i>
        </button>
        
        <div id="asisChatBox" class="asis-w-box">
            <div class="asis-w-header" id="asisHeader">
                <div class="asis-w-header-info">
                    <div class="asis-w-header-avatar">
                        <i data-lucide="bot"></i>
                    </div>
                    <div>
                        <strong>Asistente AireLab</strong>
                        <span id="asisWEstado" class="asis-w-estado">En línea</span>
                    </div>
                </div>
                <div class="asis-w-controles">
                    <button id="asisBtnMaximizar" class="asis-w-control" title="Ver completo">
                        <i data-lucide="external-link"></i>
                    </button>
                    <button id="asisBtnCerrar" class="asis-w-control" title="Cerrar">
                        <i data-lucide="x"></i>
                    </button>
                </div>
            </div>
            
            <div class="asis-w-mensajes" id="asisWMensajes">
                <div class="asis-w-msg asis-w-msg-bot">
                    <div class="asis-w-burbuja">
                        ¡Hola! Soy el asistente de AireLab. Pregúntame lo que quieras sobre la calidad del aire en Navojoa.
                    </div>
                </div>
            </div>
            
            <div class="asis-w-sugerencias">
                <button class="asis-w-sug" data-pregunta="¿Cómo está el aire?">¿Cómo está el aire?</button>
                <button class="asis-w-sug" data-pregunta="¿Qué es el PM2.5?">¿Qué es el PM2.5?</button>
                <button class="asis-w-sug" data-pregunta="¿Cómo me suscribo a alertas?">Suscribirme</button>
            </div>
            
            <form class="asis-w-form" id="asisWForm">
                <input type="text" id="asisWInput" placeholder="Escribe tu pregunta..." maxlength="300" autocomplete="off">
                <button type="submit" class="asis-w-enviar">
                    <i data-lucide="send"></i>
                </button>
            </form>
        </div>
    `;
    
    // Insertar al final del body
    const container = document.createElement('div');
    container.id = 'asistenteWidgetContainer';
    container.innerHTML = widgetHTML;
    document.body.appendChild(container);
    
    // Refrescar iconos
    if (typeof lucide !== 'undefined') {
        lucide.createIcons();
    }
    
    // ============================================
    // Referencias
    // ============================================
    const btnAbrir = document.getElementById('asisBtnAbrir');
    const chatBox = document.getElementById('asisChatBox');
    const btnCerrar = document.getElementById('asisBtnCerrar');
    const btnMaximizar = document.getElementById('asisBtnMaximizar');
    const header = document.getElementById('asisHeader');
    const mensajesDiv = document.getElementById('asisWMensajes');
    const input = document.getElementById('asisWInput');
    const form = document.getElementById('asisWForm');
    const sugerencias = document.querySelectorAll('.asis-w-sug');
    
    // ============================================
    // Abrir / Cerrar
    // ============================================
    btnAbrir.addEventListener('click', function() {
        chatBox.classList.add('asis-w-abierto');
        btnAbrir.style.display = 'none';
        input.focus();
    });
    
    btnCerrar.addEventListener('click', function() {
        chatBox.classList.remove('asis-w-abierto');
        btnAbrir.style.display = 'flex';
    });
    
    btnMaximizar.addEventListener('click', function() {
        window.location.href = '/asistente';
    });
    
    // ============================================
    // Hacer arrastrable
    // ============================================
    let isDragging = false;
    let startX, startY, initialX, initialY;
    
    header.addEventListener('mousedown', iniciarArrastre);
    header.addEventListener('touchstart', iniciarArrastre, { passive: false });
    
    function iniciarArrastre(e) {
        // No arrastrar si se clickea en botones del header
        if (e.target.closest('.asis-w-control')) return;
        
        isDragging = true;
        chatBox.classList.add('asis-w-arrastrando');
        
        const evento = e.type === 'touchstart' ? e.touches[0] : e;
        startX = evento.clientX;
        startY = evento.clientY;
        
        const rect = chatBox.getBoundingClientRect();
        initialX = rect.left;
        initialY = rect.top;
        
        document.addEventListener('mousemove', arrastrar);
        document.addEventListener('mouseup', detenerArrastre);
        document.addEventListener('touchmove', arrastrar, { passive: false });
        document.addEventListener('touchend', detenerArrastre);
        
        e.preventDefault();
    }
    
    function arrastrar(e) {
        if (!isDragging) return;
        
        const evento = e.type === 'touchmove' ? e.touches[0] : e;
        const dx = evento.clientX - startX;
        const dy = evento.clientY - startY;
        
        let nuevoX = initialX + dx;
        let nuevoY = initialY + dy;
        
        // Limites de pantalla
        const maxX = window.innerWidth - chatBox.offsetWidth;
        const maxY = window.innerHeight - chatBox.offsetHeight;
        
        nuevoX = Math.max(0, Math.min(maxX, nuevoX));
        nuevoY = Math.max(0, Math.min(maxY, nuevoY));
        
        chatBox.style.left = nuevoX + 'px';
        chatBox.style.top = nuevoY + 'px';
        chatBox.style.right = 'auto';
        chatBox.style.bottom = 'auto';
        
        e.preventDefault();
    }
    
    function detenerArrastre() {
        isDragging = false;
        chatBox.classList.remove('asis-w-arrastrando');
        document.removeEventListener('mousemove', arrastrar);
        document.removeEventListener('mouseup', detenerArrastre);
        document.removeEventListener('touchmove', arrastrar);
        document.removeEventListener('touchend', detenerArrastre);
    }
    
    // ============================================
    // Sugerencias
    // ============================================
    sugerencias.forEach(btn => {
        btn.addEventListener('click', function() {
            const pregunta = this.getAttribute('data-pregunta');
            input.value = pregunta;
            form.dispatchEvent(new Event('submit'));
        });
    });
    
    // ============================================
    // Enviar pregunta
    // ============================================
    function agregarMensaje(texto, tipo) {
        const div = document.createElement('div');
        div.className = 'asis-w-msg asis-w-msg-' + tipo;
        div.innerHTML = '<div class="asis-w-burbuja">' + texto.replace(/\n/g, '<br>') + '</div>';
        mensajesDiv.appendChild(div);
        mensajesDiv.scrollTop = mensajesDiv.scrollHeight;
    }
    
    function agregarPensando() {
        const div = document.createElement('div');
        div.className = 'asis-w-msg asis-w-msg-bot asis-w-pensando';
        div.id = 'asisWPensando';
        div.innerHTML = '<div class="asis-w-burbuja"><div class="asis-w-dots"><span></span><span></span><span></span></div></div>';
        mensajesDiv.appendChild(div);
        mensajesDiv.scrollTop = mensajesDiv.scrollHeight;
    }
    
    function quitarPensando() {
        const p = document.getElementById('asisWPensando');
        if (p) p.remove();
    }
    
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const pregunta = input.value.trim();
        if (!pregunta) return;
        
        // Ocultar sugerencias
        document.querySelector('.asis-w-sugerencias').style.display = 'none';
        
        agregarMensaje(pregunta, 'user');
        input.value = '';
        agregarPensando();
        
        try {
            const respuesta = await fetch('/api/chatbot', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pregunta: pregunta })
            });
            
            const data = await respuesta.json();
            quitarPensando();
            
            if (data.respuesta) {
                agregarMensaje(data.respuesta, 'bot');
            } else {
                agregarMensaje('Lo siento, hubo un error. Intenta de nuevo.', 'bot');
            }
        } catch (error) {
            quitarPensando();
            agregarMensaje('No pude conectarme. Verifica tu internet.', 'bot');
            console.error(error);
        }
    });
    
})();