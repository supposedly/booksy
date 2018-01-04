import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ReroutingComponent } from './rerouting.component';

describe('ReroutingComponent', () => {
  let component: ReroutingComponent;
  let fixture: ComponentFixture<ReroutingComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ReroutingComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ReroutingComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
