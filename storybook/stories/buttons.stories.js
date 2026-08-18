import govukButtonDisabledHtml from "../html/govuk-button-disabled.html?raw";
import govukButtonSecondaryHtml from "../html/govuk-button-secondary.html?raw";
import govukButtonStartHtml from "../html/govuk-button-start.html?raw";
import govukButtonWarningHtml from "../html/govuk-button-warning.html?raw";
import govukButtonHtml from "../html/govuk-button.html?raw";

export default {
  title: "GOV.UK/Button",
  parameters: {
    docs: {
      description: {
        component:
          "A button component styled according to GOV.UK design standards.",
      },
    },
  },
};

export const GovukButtonDefault = () => govukButtonHtml;
export const GovukButtonStart = () => govukButtonStartHtml;
export const GovukButtonSecondary = () => govukButtonSecondaryHtml;
export const GovukButtonWarning = () => govukButtonWarningHtml;
export const GovukButtonDisabled = () => govukButtonDisabledHtml;
