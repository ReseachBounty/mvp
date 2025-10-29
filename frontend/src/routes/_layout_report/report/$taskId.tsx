import { Container, Heading, Tabs } from "@chakra-ui/react";
import { createFileRoute, useParams } from "@tanstack/react-router";

import Overview from "@/components/Report/Overview";
import Actions from "@/components/Report/Actions";
import Analytics from "@/components/Report/Analytics";

const tabsConfig = [
  { value: "overview", title: "Overview", component: Overview },
  { value: "actions", title: "Actions", component: Actions },
  { value: "analytics", title: "Analytics", component: Analytics },
];

export const Route = createFileRoute("/_layout_report/report/$taskId")({
  component: Report,
});

function Report() {
  const { taskId } = useParams({ strict: false });


  return (
    <Container maxW="full">
      {taskId}
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} py={12}>
        Company Information
      </Heading>

      <Tabs.Root defaultValue="my-profile" variant="subtle">
        <Tabs.List>
          {tabsConfig.map((tab) => (
            <Tabs.Trigger key={tab.value} value={tab.value}>
              {tab.title}
            </Tabs.Trigger>
          ))}
        </Tabs.List>
        {tabsConfig.map((tab) => (
          <Tabs.Content key={tab.value} value={tab.value}>
            <tab.component />
          </Tabs.Content>
        ))}
      </Tabs.Root>
    </Container>
  );
}
