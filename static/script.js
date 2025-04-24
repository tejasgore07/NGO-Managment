function showContent(section) {
    const content = {
        education: {
            title: "Education and Literacy",
            text: "Our organization is working on for women and backward class by providing vocational training to hundreds of individuals in rural areas. In rural area agriculture and dairy farming are the main occupation. We are encouraging the farmers by training them about organic farming and conducting soil test. We also conduct camps and seminars for senior citizen. We surveyed villages and found that tribal communities problems and started working for them. We believe in literacy and have started library.",
            img: "static/styel/education.jpg"
        },
        agriculture: {
            title: "Agriculture",
            text: "We are working to improve agricultural practices by providing training on organic farming, soil testing, and modern farming techniques. Our goal is to increase productivity and sustainability in rural areas.",
            img: "static/styel/environment.jpg"
        },
        dalit: {
            title: "Dalit Upliftment",
            text: "Our organization is dedicated to uplifting the Dalit community by providing education, vocational training, and support for small businesses. We aim to empower individuals and promote social equality.",
            img: "static/styel/dalit.jpg"
        },
        health: {
            title: "Health and Family Welfare",
            text: "We conduct health camps, provide medical assistance, and promote awareness about health and hygiene. Our focus is on improving the overall well-being of families in rural areas.",
            img: "static/styel/health.jpg "
        },
        rural: {
            title: "Rural Development and Poverty Alleviation",
            text: "Our initiatives aim to develop rural infrastructure, provide employment opportunities, and alleviate poverty. We work closely with communities to understand their needs and implement effective solutions.",
            img: "static/styel/Rural-Devlopment (2).jpg"
        }
    };

    const mainContent = document.getElementById('main-content');
    mainContent.innerHTML = `
        <h2>${content[section].title}</h2>
        <p>${content[section].text}</p>
        <img src="${content[section].img}" alt="Image related to ${content[section].title}">
    `;

    const sidebarItems = document.querySelectorAll('.sidebar ul li');
    sidebarItems.forEach(item => item.classList.remove('active'));
    document.querySelector(`.sidebar ul li[onclick="showContent('${section}')"]`).classList.add('active');
}

