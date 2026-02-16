let cy;

const PARTY_COLORS = {
    "SP": "#ff0000",
    "SVP": "#007832",
    "FDP-Liberale": "#0044d5",
    "M-E": "#fb7203",
    "glp": "#7e3874",
    "GRÜNE": "#03f61a",
};

export function create(container, payload, dotNetRef) {
    if (typeof payload === "string") payload = JSON.parse(payload);

    cy = cytoscape({
        container,
        elements: payload.elements,
        layout: { name: "cose" },

        style: [
            {
                selector: "node",
                style: {
                    "background-color": (ele) => PARTY_COLORS[ele.data("party")] ?? "#999",
                    "border-width": 1,
                    "border-color": "#333",
                    "text-valign": "center",
                    "text-halign": "center",
                    "font-size": 10,
                    "background-blacken": -0.5, //[-1, 1[ -> -1 heller, 1 dunkler
                    "locked": true,
                }
            },
            {
                selector: "edge",
                style: {
                    width: 2,
                    "line-color": "#bbb",
                }
            },
            {
                selector: ":selected",
                style: {
                    "opacity": 1.0,
                    "background-blacken": 0,
                }
            }
        ]
    });

    cy.on('select', 'node', function (evt) {
        const node = evt.target;
        console.log(node.data('label'));
        dotNetRef.invokeMethodAsync('OnMemberSelected', {
            id: node.id(),
            label: node.data('label') ?? ''
        });
    });
}

export function hideNodes(nodes) {
    for (let i = 0; i < nodes.length; i++) {
        let node = nodes[i];
        node.style("display", "none") // versteckt die nodes + edges
    }
}

export function showNodes(nodes) {
    for (let i = 0; i < nodes.length; i++) {
        // stellt sicher, dass alle elemente, die nicht vom Filter betroffen sind gezeigt werdem
        // auch solche, die vorher betroffen waren
        let node = nodes[i];
        node.style("display", "element") // zeigt die nodes + edges
    }
}

export function search(searchText) {
    let matches = cy.nodes().filter(function (ele) {
       return ele.data('label').toLowerCase().includes(searchText.toLowerCase());
    });
    let neighborhood = matches.neighborhood();
    let nodesToShow = matches.union(neighborhood);
    let nodesToHide = cy.nodes().difference(nodesToShow);

    showNodes(nodesToShow);
    hideNodes(nodesToHide);

    if (matches.length > 0) {
        // setzt die aktuelle Auswahl auf das erste direkte Ergebnis (ohne Nachbaren)
        matches[0].select();
    }
}

export function filter(visibleParties, visibleStates) {
    let matches = cy.nodes().filter(function (ele) {
        let partyFilter = visibleParties.includes(ele.data("party"));
        let stateFilter = visibleStates.includes(ele.data("state"));
        return partyFilter && stateFilter;
    });
    let nodesToShow = matches;
    let nodesToHide = cy.nodes().difference(nodesToShow);

    showNodes(nodesToShow);
    hideNodes(nodesToHide);
}

export function dispose() {
    if (cy) {
        cy.destroy();
    }
}