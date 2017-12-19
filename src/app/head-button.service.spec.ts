import { TestBed, inject } from '@angular/core/testing';

import { ButtonService } from './button.service';

describe('ButtonService', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [ButtonService]
    });
  });

  it('should be created', inject([ButtonService], (service: ButtonService) => {
    expect(service).toBeTruthy();
  }));
});
