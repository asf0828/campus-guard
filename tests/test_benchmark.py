"""Pruebas del script de benchmark."""

import contextlib
import io
import unittest

import benchmark


class TestBenchmark(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.filas = benchmark.ejecutar(repeticiones=1)

    def test_ejecuta_todos_los_algoritmos(self):
        self.assertEqual([f.nombre for f in self.filas],
                         [nombre for nombre, _ in benchmark.ALGORITMOS])

    def test_costos_y_optimalidad(self):
        por_nombre = {f.nombre: f for f in self.filas}
        self.assertEqual(por_nombre["BFS"].resultado.costo, 17)
        self.assertEqual(por_nombre["DFS"].resultado.costo, 23)
        self.assertFalse(por_nombre["BFS"].optimo)
        self.assertFalse(por_nombre["DFS"].optimo)
        for nombre in ("A* (h nula)", "A* (h máxima)", "A* (h combinada)"):
            self.assertEqual(por_nombre[nombre].resultado.costo, 14)
            self.assertTrue(por_nombre[nombre].optimo)

    def test_tiempos_positivos(self):
        for fila in self.filas:
            self.assertGreater(fila.tiempo_ms, 0)

    def test_tabla_markdown(self):
        tabla = benchmark.tabla_markdown(self.filas)
        lineas = tabla.splitlines()
        self.assertEqual(len(lineas), 2 + len(self.filas))
        self.assertIn("Nodos expandidos", lineas[0])

    def test_linea_de_comandos(self):
        salida = io.StringIO()
        with contextlib.redirect_stdout(salida):
            codigo = benchmark.main(["--repeticiones", "1", "--formato", "csv", "--planes"])
        self.assertEqual(codigo, 0)
        texto = salida.getvalue()
        self.assertIn("Algoritmo,Acciones,Costo", texto)
        self.assertIn("BFS: AJUSTE_CARGA", texto)

    def test_estado_inicial_invalido(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                benchmark.main(["--inicial", "11", "8", "4", "0", "0", "--repeticiones", "1"])


if __name__ == "__main__":
    unittest.main()
