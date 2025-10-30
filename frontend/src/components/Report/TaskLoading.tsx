import { ReportService } from "@/client";
import {
  Box,
  Button,
  Flex,
  Icon,
  Progress,
  Spinner,
  Text,
  VStack,
} from "@chakra-ui/react";
import { useNavigate } from "@tanstack/react-router";
import { useTheme } from 'next-themes';
import { useEffect, useState } from "react";
import { FiAlertCircle } from "react-icons/fi";

// Mapping degli status del backend
type TaskStatus = "pending" | "running" | "completed" | "failed";

interface TaskStatusInfo {
  label: string;
  progress: number;
  color: string;
}

const STATUS_MAP: Record<TaskStatus, TaskStatusInfo> = {
  pending: {
    label: "Inizializzazione in corso...",
    progress: 10,
    color: "blue.500",
  },
  running: {
    label: "Analisi in corso - Raccolta dati e generazione report",
    progress: 50,
    color: "blue.500",
  },
  completed: {
    label: "Report completato con successo!",
    progress: 100,
    color: "green.500",
  },
  failed: {
    label: "Errore durante la generazione del report",
    progress: 100,
    color: "red.500",
  },
};

interface ProcessOverlayProps {
    taskId: string;
    isOpen: boolean;
    onClose?: () => void;
}

export default function TaskLoading({
    taskId,
    isOpen,
    onClose,
}: ProcessOverlayProps) {
    const navigate = useNavigate();

  const [currentStatus, setCurrentStatus] = useState<TaskStatus>("pending");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const { theme } = useTheme();
  const overlayBg = theme === 'light' ? "blackAlpha.700" : "blackAlpha.800";

    useEffect(() => {
      if (!isOpen) return;
      let interval: NodeJS.Timeout;

      const pollStatus = async () => {
        try {
          const response = await ReportService.readTask({ taskId });
          const status = response.status as TaskStatus;

          setCurrentStatus(status);

          if (status === "completed") {
            clearInterval(interval);
            // Piccolo delay per mostrare il messaggio di successo
            setTimeout(() => {
              navigate({ to: "/report/$taskId", params: { taskId } });
            }, 1500);
          } else if (status === "failed") {
            clearInterval(interval);
            setErrorMessage("Si è verificato un errore imprevisto");
          }
        } catch (err) {
          console.error("Errore durante polling:", err);
          setErrorMessage("Impossibile recuperare lo stato del task");
        }
      };

      // Poll iniziale e poi ogni 3 secondi
      pollStatus();
      interval = setInterval(pollStatus, 3000);

      return () => clearInterval(interval);
    }, [isOpen, taskId, navigate]);

  if (!isOpen) return null;

  const statusInfo = STATUS_MAP[currentStatus];
  const progress = statusInfo.progress;

  return (
    <Flex
      position="fixed"
      top={0}
      left={0}
      w="100vw"
      h="100vh"
      bg={overlayBg}
      backdropFilter="blur(4px)"
      zIndex={9999}
      align="center"
      justify="center"
    >
      <Box
        bg="white"
        p={8}
        borderRadius="2xl"
        boxShadow="xl"
        w="md"
        textAlign="center"
      >
        <VStack gap={4}>
          {currentStatus === "failed" ? (
            <Icon fontSize="4xl" color="red.500">
              <FiAlertCircle />
            </Icon>
          ) : (
            <Spinner size="xl" color={statusInfo.color} />
          )}

          <Text fontSize="xl" fontWeight="semibold" color={statusInfo.color}>
            {statusInfo.label}
          </Text>

          {errorMessage && (
            <Text fontSize="sm" color="red.600" px={4}>
              {errorMessage}
            </Text>
          )}

          {currentStatus !== "failed" && (
            <>
              <Progress.Root
                value={progress}
                size="sm"
                colorScheme={currentStatus === "completed" ? "green" : "blue"}
                borderRadius="md"
                w="full"
                striped
                animated={currentStatus !== "completed"}
              />
              <Text fontSize="sm" color="gray.500">
                {Math.round(progress)}% completato
              </Text>
            </>
          )}

          {currentStatus === "running" && (
            <Text fontSize="xs" color="gray.400" mt={2}>
              Questo processo può richiedere alcuni minuti...
            </Text>
          )}

          {currentStatus === "failed" && onClose && (
            <Button
              mt={4}
              colorScheme="red"
              variant="outline"
              onClick={onClose}
            >
              Chiudi
            </Button>
          )}
        </VStack>
      </Box>
    </Flex>
  );
}
