const baseurl = "https://127.0.0.1:5000";

module.exports = {
  defaults: {
    timeout: 2000,
    useIncognitoBrowserContext: false,
    chromeLaunchConfig: {
      ignoreHTTPSErrors: true,
    },
    viewport: {
      width: 1280,
      height: 1080,
    },
    userAgent: "A11Y TESTS",
  },
  urls: [
    // static pages
    `${baseurl}/how-to-use-this-service`,
    `${baseurl}/terms-of-use`,
    `${baseurl}/privacy`,
    `${baseurl}/cookies`,
    `${baseurl}/accessibility`,
    `${baseurl}/signed-out`,
    `${baseurl}/`,

    // authentication steps
    `${baseurl}/sign-out`,
    {
      url: `${baseurl}/sign-in`,
      actions: [
        "wait for element #username to be visible",
        `set field #username to ${process.env.AYR_AAU_USER_USERNAME}`,
        `set field #password to ${process.env.AYR_AAU_USER_PASSWORD}`,
        'click element button[type="submit"]',
        "wait for path to be /browse",
      ],
    },

    // pages that require authentication
    `${baseurl}/browse`,
    `${baseurl}/browse/series/1d4cedb8-95f5-4e5e-bc56-c0c0f6cccbd7`,
    `${baseurl}/browse/consignment/b4a8379c-0767-4a9b-8537-181aed23e837`,
    `${baseurl}/record/100251bb-5b93-48a9-953f-ad5bd9abfbdc`,
    `${baseurl}/search_results_summary?query=test`,
    `${baseurl}/search/transferring_body/` +
      "c3e3fd83-4d52-4638-a085-1f4e4e4dfa50" +
      `?query=test`,
  ],
};
