let cy;

// Diagonal hatch (Schraffur) as a tileable SVG data URI, coloured per node.
function hatch(color) {
    const svg =
        "<svg xmlns='http://www.w3.org/2000/svg' width='8' height='8'>" +
        "<path d='M0,8 L8,0 M-2,2 L2,-2 M6,10 L10,6' stroke='" + color + "' stroke-width='1.5'/>" +
        "</svg>";
    return "data:image/svg+xml;utf8," + encodeURIComponent(svg);
}


export function create(container, payload, dotNetRef) {
    if (typeof payload === "string") payload = JSON.parse(payload);


    cy = cytoscape({
        container,
        elements: payload.elements,
        layout: {
            name: 'cose-bilkent',
            idealEdgeLength: 150,
            nodeRepulsion: 6000,
            gravity: 0.25,
        },

        style: [
        {
            selector: "node",
            style: {
            "background-color": (ele) => ele.data("color"),
            "border-width": 3,
            "border-color": "#ffffff",
            "border-opacity": 1,
            "text-valign": "center",
            "text-halign": "center",
            "font-size": 10,
            },
        },
        {
            selector: 'node[state = "Inaktiv"]',
            style: {
                "background-color": "#ffffff",
                "background-image": (ele) => hatch(ele.data("color")),
                "background-repeat": "repeat",
                "background-width": "8px",
                "background-height": "8px",
                "background-fit": "none",
                "border-style": "dotted",
                "border-color": (ele) => ele.data("color"),
                "border-width": 2,
            },
        },
        {
            selector: "edge",
            style: { width: 2, "line-color": "#c3cad9" },
        },
        {
            selector: "node.hovered",
            style: {
                "underlay-color": "#6366f1",
                "underlay-opacity": 0.18,
                "underlay-padding": 5,
            },
        },
        {
            selector: "node:selected",
            style: {
                "underlay-color": "#6366f1",
                "underlay-opacity": 0.3,
                "underlay-padding": 7,
            },
        },
        ]
    });

    cy.on('select', 'node', function (evt) {
        const node = evt.target;
        dotNetRef.invokeMethodAsync('OnMemberSelected', {
            id: node.id(),
            label: node.data('label') ?? '',
        });
    });

    cy.on('unselect', 'node', function () {
        // Guard gegen fälschliches feuern, wenn A->B
        setTimeout(() => {
            if (cy.$(':selected').length === 0) {
                dotNetRef.invokeMethodAsync('OnMemberDeselected');
            }
        }, 50);
    });

    cy.on('layoutstop', () => {
        cy.autolock(true);
    });

    cy.on('mouseover', 'node', (e) => e.target.addClass('hovered'));
    cy.on('mouseout',  'node', (e) => e.target.removeClass('hovered'));
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

export function search(searchText, visibleParties, visibleStates) {

    cy.elements().unselect();

    if (searchText.trim() === "") {
        cy.animate({
            zoom: 0.25,
            center: { eles: cy.elements() }
        }, { duration: 300 });
        return;
    }

    let matches = cy.nodes().filter(function (ele) {
        let nameFilter = ele.data('label').toLowerCase().includes(searchText.toLowerCase());
        let partyFilter = visibleParties.includes(ele.data("party_group"));
        let stateFilter = visibleStates.includes(ele.data("state"));
        return partyFilter && stateFilter && nameFilter;
    });

    if (matches.length > 0) {
        let firstMatch = matches[0];
        // setzt die aktuelle Auswahl auf das erste direkte Ergebnis (ohne Nachbaren)
        firstMatch.select();
        cy.animate({
            zoom: 1.0,
            center: { eles: firstMatch }
        }, { duration: 300 });
    }
}

export function filter(visibleParties, visibleStates) {
    console.log(visibleParties);
    let matches = cy.nodes().filter(function (ele) {
        let partyFilter = visibleParties.includes(ele.data("party_group"));
        let stateFilter = visibleStates.includes(ele.data("state"));
        return partyFilter && stateFilter;
    });
    let nodesToShow = matches;
    let nodesToHide = cy.nodes().difference(nodesToShow);

    showNodes(nodesToShow);
    hideNodes(nodesToHide);
}

export function deselect() {
    if (cy) cy.elements().unselect();
}

export function dispose() {
    if (cy) {
        cy.destroy();
    }
}