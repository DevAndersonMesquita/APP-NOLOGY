let tipoCliente = 'comum'

function selecionarCliente(tipo) {
    tipoCliente = tipo
}

async function calcularCashback() {
    const valor = document.getElementById('valor').value
    const desconto = document.getElementById('desconto').value
    const cliente = document.getElementById('Cliente').value
    const vip = cliente === 'VIP'

    const response = await fetch(`https://app-nology.onrender.com/cashback?valor_compra=${valor}&desconto=${desconto}&vip=${vip}`)
    const data = await response.json()

    document.getElementById('Resultado').innerText = `Seu cashback: R$ ${data.cashback}`

    carregarHistorico()
}

async function carregarHistorico() {
    const response = await fetch('https://app-nology.onrender.com/historico')
    const data = await response.json()

    const tabela = document.getElementById('tabela-historico')
    tabela.innerHTML = ''

    data.historico.forEach(item => {
        tabela.innerHTML += `
            <tr>
                <td>${item.tipo_cliente}</td>
                <td>R$ ${item.valor_compra}</td>
                <td>${item.desconto}%</td>
                <td>R$ ${item.cashback}</td>
            </tr>
        `
    })
}

carregarHistorico()