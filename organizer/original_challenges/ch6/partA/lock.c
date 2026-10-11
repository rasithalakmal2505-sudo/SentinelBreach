#include <stdio.h>
#include <string.h>

/* Legacy access-check utility recovered from a ShadowTrace-linked host.
 * "asks for a key" - per the README given to players. */

static const unsigned char stored[] = {0x3d, 0x32, 0x6a, 0x29, 0x2e, 0x05, 0x6b, 0x34, 0x05, 0x2e, 0x32, 0x69, 0x05, 0x2d, 0x6b, 0x28, 0x69};
static const unsigned char xor_key = 0x5a;

int main(void) {
    char input[128];

    printf("Enter key: ");
    if (!fgets(input, sizeof(input), stdin)) {
        return 1;
    }
    input[strcspn(input, "\n")] = '\0';

    size_t len = strlen(input);
    if (len != sizeof(stored)) {
        printf("Access denied.\n");
        return 1;
    }

    unsigned char transformed[128];
    for (size_t i = 0; i < len; i++) {
        transformed[i] = (unsigned char)input[i] ^ xor_key;
    }

    if (memcmp(transformed, stored, len) == 0) {
        printf("Access granted.\n");
        return 0;
    }

    printf("Access denied.\n");
    return 1;
}
