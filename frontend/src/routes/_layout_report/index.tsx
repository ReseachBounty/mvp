import { createFileRoute } from "@tanstack/react-router";
import {
  Box,
  Container,
  Text,
  Heading,
  Flex,
  Button,
  HStack,
  SimpleGrid,
  Link,
  List,
} from "@chakra-ui/react";

import { LinkButton } from "@/components/ui/link-button";

export const Route = createFileRoute("/_layout_report/")({
  component: LandingPage,
});

export default function LandingPage() {
  const textMuted = "fg.muted";
  const cardBg = "bg.surface";
  const bg = "bg.canvas";

  return (
    <>
      <Box bg={bg} color="fg.default" minH="100vh">
        {/* Hero */}
        <Container maxW="6xl" py={12}>
          <SimpleGrid columns={{ base: 1, lg: 2 }} alignItems="center">
            <Box>
              <Heading as="h2" size="2xl" lineHeight="short">
                Posiziona il tuo prodotto dove conta di più
              </Heading>
              <Text mt={4} color={textMuted}>
                Analizziamo la presenza digitale del tuo prodotto o servizio con
                tecnologie AI all'avanguardia e ti forniamo un report in 3 fasi
                — Overview, Actions e Analitics — per migliorare la percezione e
                la performance sul mercato.
              </Text>
              <HStack mt={6}>
                <LinkButton
                  href="/company-info"
                  variant="solid"
                  colorPalette="teal"
                >
                  Prova ora
                </LinkButton>
              </HStack>
            </Box>

            <Box
              p={6}
              rounded="2xl"
              shadow="sm"
              bgGradient="to-br"
              gradientFrom="teal.100"
              gradientTo="yellow.50"
            >
              <Box bg={cardBg} p={4} rounded="xl">
                <Heading as="h3" size="md">
                  Preview del report
                </Heading>
                <List.Root mt={3} fontSize="sm" color={textMuted}>
                  <List.Item>
                    <b>Overview</b> — Analisi del posizionamento attuale:
                    messaggio, audience, prezzi, posizionamento competitivo.
                  </List.Item>
                  <List.Item>
                    <b>Actions</b> — 7 raccomandazioni pratiche e prioritarie:
                    messaging, canali, ottimizzazioni prodotto.
                  </List.Item>
                  <List.Item>
                    <b>Analitics</b> — KPI proposti, metriche da monitorare e
                    roadmap per test A/B.
                  </List.Item>
                </List.Root>
                <HStack mt={4}>
                  <LinkButton
                    as={Link}
                    href="/company-info"
                    variant="solid"
                    colorPalette="teal"
                  >
                    Testa gratis
                  </LinkButton>
                </HStack>
              </Box>
            </Box>
          </SimpleGrid>
        </Container>

        {/* Footer */}
        <Container maxW="6xl" py={12}>
          <Flex
            direction={{ base: "column", md: "row" }}
            align="center"
            justify="space-between"
            bg="bg.subtle"
            p={8}
            rounded="2xl"
            gap={6}
          >
            <Box>
              <Heading as="h4" size="md">
                Pronto a scoprire il posizionamento ottimale del tuo prodotto?
              </Heading>
              <Text color={textMuted} mt={2}>
                Richiedi ora un report gratuito e ricevi un PDF dettagliato con
                Overview, Actions e Analitics.
              </Text>
            </Box>
            <HStack>
              <LinkButton
                as={Link}
                href="/company-info"
                variant="solid"
                colorPalette="teal"
              >
                Sii fra i primi
              </LinkButton>
              <Button as={Link} variant="outline" color={textMuted}>
                Contattaci
              </Button>
            </HStack>
          </Flex>
        </Container>
      </Box>
    </>
  );
}
