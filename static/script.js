let selectedCarr = []; // Variável global para os carregamentos selecionados
let modalOpen = false; // Variável para rastrear se um modal está aberto

document.addEventListener("keypress", function(event) {
    if (!modalOpen && event.key === "Enter") { // Desabilita ENTER se o modal estiver aberto
        event.preventDefault();

        selectedCarr = []; // Reinicializar a variável global
        document.querySelectorAll(".row-checkbox:checked").forEach(checkbox => {
            selectedCarr.push(checkbox.value);
        });

        fetch('/process_selected', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ selected: selectedCarr })
        })
        .then(response => response.json())
        .then(data => {
            if (data.unique_machines) {
                // Exibir o modal para selecionar as máquinas
                showMachinesModal(data.unique_machines);
            } else if (data.report_html) {
                // Exibir o relatório em um modal
                showReportModal(data.report_html);
            }
        })
        .catch(err => console.error("Erro ao enviar:", err));
    }
});

document.addEventListener("keydown", function(event) {
    if (event.key === "Escape") {
        if (modalOpen) {
            // Fechar o modal
            closeModal();
        } else {
            // Desmarcar checkboxes na tela inicial
            document.querySelectorAll(".row-checkbox:checked").forEach(checkbox => {
                checkbox.checked = false;
            });
        }
    }
});

function showMachinesModal(machines) {
    modalOpen = true; // Indicar que o modal está aberto
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h3>Selecione as Máquinas:</h3>
            ${machines.map(machine => `
                <label>
                    <input type="checkbox" class="machine-checkbox" value="${machine}">
                    ${machine}
                </label>
            `).join('')}
            <button id="submit-machines">Confirmar</button>
        </div>
    `;
    document.body.appendChild(modal);

    document.getElementById("submit-machines").onclick = function() {
        const selectedMachines = [];
        document.querySelectorAll(".machine-checkbox:checked").forEach(checkbox => {
            selectedMachines.push(checkbox.value);
        });

        // Enviar máquinas selecionadas para o servidor
        fetch('/process_selected', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                selected: selectedCarr,  // Utilizar a variável global aqui
                selected_machines: selectedMachines
            })
        })
        .then(response => response.json())
        .then(data => {
            closeModal(); // Fechar o modal de seleção de máquinas antes de abrir o próximo
            if (data.report_html) {
                // Exibir o relatório em um modal
                showReportModal(data.report_html);
            }
        })
        .catch(err => console.error("Erro ao enviar máquinas:", err));
    };
}

function showReportModal(reportHtml) {
    modalOpen = true; // Indicar que o modal está aberto
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h3>Relatório</h3>
            <div>
                ${reportHtml}
            </div>
            <button id="close-report-modal">Fechar</button>
        </div>
    `;
    document.body.appendChild(modal);

    document.getElementById("close-report-modal").onclick = function() {
        closeModal();
    };
}

function closeModal() {
    modalOpen = false; // Indicar que o modal foi fechado
    document.querySelectorAll('.modal').forEach(modal => modal.remove());
}
